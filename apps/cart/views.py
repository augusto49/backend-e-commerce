"""
Views for the cart app.
Views para o app de carrinho.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.coupons.models import Coupon
from apps.core.exceptions import InsufficientStockException, InvalidCouponException
from apps.products.models import Product, ProductVariation, Stock

from .models import Cart, CartItem
from .serializers import (
    ApplyCouponSerializer,
    CartItemCreateSerializer,
    CartItemSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
)


class CartMixin:
    """
    Mixin to get or create cart.
    Mixin para obter ou criar carrinho.
    """

    def get_cart(self, request):
        """
        Get or create cart for user or session.
        Obtém ou cria carrinho para usuário ou sessão.
        """
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            # Merge session cart if exists
            # Mescla carrinho da sessão se existir
            if created:
                session_key = request.session.session_key
                if session_key:
                    session_cart = Cart.objects.filter(
                        session_key=session_key,
                        user__isnull=True,
                    ).first()
                    if session_cart:
                        for item in session_cart.items.all():
                            try:
                                cart_item = cart.items.get(
                                    product=item.product,
                                    variation=item.variation,
                                )
                                cart_item.quantity += item.quantity
                                cart_item.save()
                            except CartItem.DoesNotExist:
                                item.cart = cart
                                item.save()
                        session_cart.delete()
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key,
                user__isnull=True,
            )
        return cart


class CartView(CartMixin, APIView):
    """
    Get current cart.
    Obtém carrinho atual.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response({"success": True, "data": serializer.data})


class CartItemView(CartMixin, APIView):
    """
    Add item to cart.
    Adiciona item ao carrinho.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart(request)
        product_id = serializer.validated_data["product_id"]
        variation_id = serializer.validated_data.get("variation_id")
        quantity = serializer.validated_data["quantity"]

        # Get product
        # Obtém produto
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get variation if provided
        # Obtém variação se fornecida
        variation = None
        if variation_id:
            try:
                variation = ProductVariation.objects.get(
                    id=variation_id,
                    product=product,
                    is_active=True,
                )
            except ProductVariation.DoesNotExist:
                return Response(
                    {"success": False, "message": "Variation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Check stock
        # Verifica estoque
        stock = Stock.objects.filter(
            product=product,
            variation=variation,
        ).first()

        if stock and stock.available_quantity < quantity:
            raise InsufficientStockException(
                f"Only {stock.available_quantity} items available."
            )

        # Add or update cart item
        # Adiciona ou atualiza item do carrinho
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variation=variation,
            defaults={
                "quantity": quantity,
                "unit_price": variation.final_price if variation else product.current_price,
            },
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            {
                "success": True,
                "message": "Item added to cart.",
                "data": CartSerializer(cart).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(CartMixin, APIView):
    """
    Update or remove cart item.
    Atualiza ou remove item do carrinho.
    """

    permission_classes = [permissions.AllowAny]

    def get_cart_item(self, cart, item_id):
        try:
            return cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return None

    def patch(self, request, item_id):
        """
        Update cart item quantity.
        Atualiza quantidade do item do carrinho.
        """
        cart = self.get_cart(request)
        cart_item = self.get_cart_item(cart, item_id)

        if not cart_item:
            return Response(
                {"success": False, "message": "Item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]

        # Check stock
        # Verifica estoque
        stock = Stock.objects.filter(
            product=cart_item.product,
            variation=cart_item.variation,
        ).first()

        if stock and stock.available_quantity < quantity:
            raise InsufficientStockException(
                f"Only {stock.available_quantity} items available."
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response(
            {
                "success": True,
                "message": "Cart updated.",
                "data": CartSerializer(cart).data,
            }
        )

    def delete(self, request, item_id):
        """
        Remove item from cart.
        Remove item do carrinho.
        """
        cart = self.get_cart(request)
        cart_item = self.get_cart_item(cart, item_id)

        if not cart_item:
            return Response(
                {"success": False, "message": "Item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()

        return Response(
            {
                "success": True,
                "message": "Item removed from cart.",
                "data": CartSerializer(cart).data,
            }
        )


class CartCouponView(CartMixin, APIView):
    """
    Apply or remove coupon from cart.
    Aplica ou remove cupom do carrinho.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Apply coupon to cart.
        Aplica cupom ao carrinho.
        """
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart(request)
        code = serializer.validated_data["code"]

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            raise InvalidCouponException("Coupon not found.")

        if not coupon.is_valid:
            raise InvalidCouponException("This coupon is expired or inactive.")

        if cart.subtotal < coupon.min_order_value:
            raise InvalidCouponException(
                f"Minimum order value for this coupon is R$ {coupon.min_order_value}."
            )

        cart.coupon = coupon
        cart.save()

        return Response(
            {
                "success": True,
                "message": "Coupon applied successfully.",
                "data": CartSerializer(cart).data,
            }
        )

    def delete(self, request):
        """
        Remove coupon from cart.
        Remove cupom do carrinho.
        """
        cart = self.get_cart(request)
        cart.coupon = None
        cart.save()

        return Response(
            {
                "success": True,
                "message": "Coupon removed.",
                "data": CartSerializer(cart).data,
            }
        )


class CartClearView(CartMixin, APIView):
    """
    Clear all items from cart.
    Limpa todos os itens do carrinho.
    """

    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        cart = self.get_cart(request)
        cart.clear()

        return Response(
            {
                "success": True,
                "message": "Cart cleared.",
                "data": CartSerializer(cart).data,
            }
        )
