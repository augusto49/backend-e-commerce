"""
Views for the payments app.
Views para o app de pagamentos.
"""

import json

from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import BusinessLogicException, PaymentFailedException
from apps.orders.models import Order, OrderStatusHistory

from .gateways.mercadopago import MercadoPagoGateway
from .gateways.stripe import StripeGateway
from .models import Payment, PaymentTransaction
from .serializers import CreatePaymentSerializer, PaymentSerializer, RefundSerializer


class PaymentGatewayMixin:
    """
    Mixin to get payment gateway.
    Mixin para obter gateway de pagamento.
    """

    def get_gateway(self, gateway_name: str):
        gateways = {
            "mercadopago": MercadoPagoGateway,
            "stripe": StripeGateway,
            # "pagseguro": PagSeguroGateway,
        }
        gateway_class = gateways.get(gateway_name)
        if not gateway_class:
            raise BusinessLogicException(f"Gateway {gateway_name} not supported.")
        return gateway_class()


class CreatePaymentView(PaymentGatewayMixin, APIView):
    """
    Create a payment for an order.
    Cria um pagamento para um pedido.
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get order
        # Obtém pedido
        try:
            order = Order.objects.get(
                id=serializer.validated_data["order_id"],
                user=request.user,
            )
        except Order.DoesNotExist:
            raise BusinessLogicException("Order not found.")

        if order.status not in ["pending", "awaiting_payment"]:
            raise BusinessLogicException("Order is not awaiting payment.")

        # Get gateway
        # Obtém gateway
        gateway = self.get_gateway(serializer.validated_data["gateway"])

        # Create payment in our system
        # Cria pagamento no nosso sistema
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            gateway=serializer.validated_data["gateway"],
            method=serializer.validated_data["method"],
            amount=order.total,
            status="pending",
        )

        # Process payment with gateway
        # Processa pagamento com gateway
        customer_data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "cpf": request.user.cpf,
        }

        result = gateway.create_payment(
            order_id=order.id,
            amount=order.total,
            payment_method=serializer.validated_data["method"],
            customer_data=customer_data,
            card_token=serializer.validated_data.get("card_token"),
            payment_method_id=serializer.validated_data.get("payment_method_id"),
            installments=serializer.validated_data.get("installments", 1),
        )

        if not result.success:
            payment.status = "rejected"
            payment.gateway_response = {"error": result.error}
            payment.save()
            raise PaymentFailedException(result.message)

        # Update payment with gateway response
        # Atualiza pagamento com resposta do gateway
        payment.gateway_payment_id = result.payment_id
        payment.status = result.status
        payment.gateway_status = result.data.get("gateway_status", "")
        payment.gateway_response = result.data

        if result.data:
            payment.pix_qr_code = result.data.get("pix_qr_code", "")
            payment.pix_qr_code_base64 = result.data.get("pix_qr_code_base64", "")
            payment.boleto_url = result.data.get("boleto_url", "")
            payment.boleto_barcode = result.data.get("boleto_barcode", "")

        payment.save()

        # Update order status
        # Atualiza status do pedido
        if result.status == "approved":
            order.status = "paid"
        else:
            order.status = "awaiting_payment"
        order.save()

        # Record transaction
        # Registra transação
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type="authorization",
            status=result.status,
            amount=order.total,
            gateway_transaction_id=result.payment_id or "",
            gateway_response=result.data,
        )

        return Response(
            {
                "success": True,
                "message": "Payment processed.",
                "data": PaymentSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentDetailView(APIView):
    """
    Get payment details.
    Obtém detalhes do pagamento.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {"success": False, "message": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": PaymentSerializer(payment).data}
        )


class RefundPaymentView(PaymentGatewayMixin, APIView):
    """
    Request refund for a payment.
    Solicita reembolso de um pagamento.
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, payment_id):
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user,
            )
        except Payment.DoesNotExist:
            raise BusinessLogicException("Payment not found.")

        if payment.status != "approved":
            raise BusinessLogicException("Only approved payments can be refunded.")

        gateway = self.get_gateway(payment.gateway)
        result = gateway.refund(
            payment_id=payment.gateway_payment_id,
            amount=serializer.validated_data.get("amount"),
            reason=serializer.validated_data.get("reason", ""),
        )

        if not result.success:
            raise BusinessLogicException(result.message)

        # Update payment
        # Atualiza pagamento
        payment.status = "refunded"
        payment.refund_reason = serializer.validated_data.get("reason", "")
        from django.utils import timezone

        payment.refunded_at = timezone.now()
        payment.save()

        # Update order
        # Atualiza pedido
        payment.order.status = "refunded"
        payment.order.save()

        return Response(
            {
                "success": True,
                "message": "Refund processed successfully.",
                "data": PaymentSerializer(payment).data,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class MercadoPagoWebhookView(PaymentGatewayMixin, APIView):
    """
    Handle Mercado Pago webhooks.
    Lida com webhooks do Mercado Pago.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            gateway = MercadoPagoGateway()
            result = gateway.process_webhook(request.data)

            if "error" in result:
                return HttpResponse(status=400)

            if "id" in result and "status" in result:
                payment = Payment.objects.filter(
                    gateway_payment_id=str(result["id"])
                ).first()

                if payment and payment.status != result["status"]:
                    payment.status = result["status"]
                    payment.save()

                    # Update order if payment approved
                    # Atualiza pedido se pagamento aprovado
                    if result["status"] == "approved":
                        payment.order.status = "paid"
                        payment.order.save()

                        OrderStatusHistory.objects.create(
                            order=payment.order,
                            status="paid",
                            notes="Payment confirmed via webhook",
                        )

            return HttpResponse(status=200)

        except Exception:
            return HttpResponse(status=500)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(PaymentGatewayMixin, APIView):
    """
    Handle Stripe webhooks.
    Lida com webhooks do Stripe.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            gateway = StripeGateway()
            signature = request.headers.get("Stripe-Signature")
            result = gateway.process_webhook(request.body, signature)

            if "error" in result:
                return HttpResponse(status=400)

            if "id" in result and "status" in result:
                payment = Payment.objects.filter(
                    gateway_payment_id=result["id"]
                ).first()

                if payment and payment.status != result["status"]:
                    payment.status = result["status"]
                    payment.save()

                    if result["status"] == "approved":
                        payment.order.status = "paid"
                        payment.order.save()

            return HttpResponse(status=200)

        except Exception:
            return HttpResponse(status=500)
