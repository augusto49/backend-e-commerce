"""
Views for the orders app.
Views para o app de pedidos.
"""

from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.cart.models import Cart
from apps.core.exceptions import BusinessLogicException, CartEmptyException
from apps.core.permissions import IsAdminUser, IsOwner
from apps.coupons.models import CouponUsage
from apps.products.models import Stock

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    CheckoutSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderStatusUpdateSerializer,
)
from .tasks import send_order_confirmation_email


class CheckoutView(APIView):
    """
    Create order from cart.
    Cria pedido a partir do carrinho.
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get cart
        # Obtém carrinho
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            raise CartEmptyException()

        if cart.items.count() == 0:
            raise CartEmptyException()

        # Get addresses
        # Obtém endereços
        try:
            shipping_address = Address.objects.get(
                id=serializer.validated_data["shipping_address_id"],
                user=request.user,
            )
        except Address.DoesNotExist:
            raise BusinessLogicException("Shipping address not found.")

        billing_address = shipping_address
        if serializer.validated_data.get("billing_address_id"):
            try:
                billing_address = Address.objects.get(
                    id=serializer.validated_data["billing_address_id"],
                    user=request.user,
                )
            except Address.DoesNotExist:
                raise BusinessLogicException("Billing address not found.")

        # Create order
        # Cria pedido
        order = Order.objects.create(
            user=request.user,
            status="pending",
            shipping_address={
                "recipient_name": shipping_address.recipient_name,
                "street": shipping_address.street,
                "number": shipping_address.number,
                "complement": shipping_address.complement,
                "neighborhood": shipping_address.neighborhood,
                "city": shipping_address.city,
                "state": shipping_address.state,
                "zipcode": shipping_address.zipcode,
                "phone": shipping_address.phone,
            },
            billing_address={
                "recipient_name": billing_address.recipient_name,
                "street": billing_address.street,
                "number": billing_address.number,
                "complement": billing_address.complement,
                "neighborhood": billing_address.neighborhood,
                "city": billing_address.city,
                "state": billing_address.state,
                "zipcode": billing_address.zipcode,
            },
            subtotal=cart.subtotal,
            shipping_cost=0,  # TODO: Calculate from shipping method
            # TODO: Calcular a partir do método de envio
            discount=cart.discount,
            total=cart.total,
            coupon=cart.coupon,
            coupon_code=cart.coupon.code if cart.coupon else "",
            shipping_method=serializer.validated_data["shipping_method"],
            customer_notes=serializer.validated_data.get("customer_notes", ""),
        )

        # Create order items and update stock
        # Cria itens do pedido e atualiza estoque
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variation=cart_item.variation,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                variation_name=cart_item.variation.name if cart_item.variation else "",
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
            )

            # Reserve stock
            # Reserva estoque
            stock = Stock.objects.filter(
                product=cart_item.product,
                variation=cart_item.variation,
            ).first()

            if stock:
                stock.reserved_quantity += cart_item.quantity
                stock.save()

            # Increment order count on product
            # Incrementa contagem de pedidos no produto
            cart_item.product.order_count += cart_item.quantity
            cart_item.product.save(update_fields=["order_count"])

        # Record coupon usage
        # Registra uso do cupom
        if cart.coupon:
            CouponUsage.objects.create(
                coupon=cart.coupon,
                user=request.user,
                order=order,
            )
            cart.coupon.times_used += 1
            cart.coupon.save(update_fields=["times_used"])

        # Create initial status history
        # Cria histórico inicial de status
        OrderStatusHistory.objects.create(
            order=order,
            status="pending",
            notes="Order created",
            created_by=request.user,
        )

        # Clear cart
        # Limpa carrinho
        cart.clear()

        # Send confirmation email
        # Envia email de confirmação
        send_order_confirmation_email.delay(order.id)

        return Response(
            {
                "success": True,
                "message": "Order created successfully.",
                "data": OrderDetailSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user orders.
    ViewSet para pedidos do usuário.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel an order.
        Cancela um pedido.
        """
        order = self.get_object()

        if not order.can_cancel:
            return Response(
                {"success": False, "message": "This order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Release reserved stock
            # Libera estoque reservado
            for item in order.items.all():
                stock = Stock.objects.filter(
                    product=item.product,
                    variation=item.variation,
                ).first()
                if stock:
                    stock.reserved_quantity = max(
                        0, stock.reserved_quantity - item.quantity
                    )
                    stock.save()

            order.status = "cancelled"
            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status="cancelled",
                notes="Cancelled by customer",
                created_by=request.user,
            )

        return Response(
            {
                "success": True,
                "message": "Order cancelled successfully.",
                "data": OrderDetailSerializer(order).data,
            }
        )


# Admin ViewSet
class OrderAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for order management.
    ViewSet de admin para gerenciamento de pedidos.
    """

    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderListSerializer

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """
        Update order status.
        Atualiza status do pedido.
        """
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        notes = serializer.validated_data.get("notes", "")
        tracking_code = serializer.validated_data.get("tracking_code")

        with transaction.atomic():
            order.status = new_status
            if tracking_code:
                order.tracking_code = tracking_code
            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                created_by=request.user,
            )

            # Handle stock on status changes
            # Lida com estoque em mudanças de status
            if new_status == "shipped":
                for item in order.items.all():
                    stock = Stock.objects.filter(
                        product=item.product,
                        variation=item.variation,
                    ).first()
                    if stock:
                        stock.quantity -= item.quantity
                        stock.reserved_quantity -= item.quantity
                        stock.save()

        return Response(
            {
                "success": True,
                "message": "Order status updated.",
                "data": OrderDetailSerializer(order).data,
            }
        )
