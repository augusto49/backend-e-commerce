"""
Mercado Pago payment gateway integration.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings

from .base import BasePaymentGateway, PaymentResult, RefundResult

logger = logging.getLogger(__name__)


class MercadoPagoGateway(BasePaymentGateway):
    """
    Mercado Pago payment gateway.
    """

    def __init__(self):
        self.access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        self._sdk = None

    @property
    def sdk(self):
        """Lazy load Mercado Pago SDK."""
        if self._sdk is None:
            import mercadopago

            self._sdk = mercadopago.SDK(self.access_token)
        return self._sdk

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_method: str,
        customer_data: Dict[str, Any],
        **kwargs,
    ) -> PaymentResult:
        """Create a payment with Mercado Pago."""
        try:
            payment_data = {
                "transaction_amount": float(amount),
                "description": f"Order #{order_id}",
                "external_reference": str(order_id),
                "payer": {
                    "email": customer_data.get("email"),
                    "first_name": customer_data.get("first_name"),
                    "last_name": customer_data.get("last_name"),
                    "identification": {
                        "type": "CPF",
                        "number": customer_data.get("cpf", ""),
                    },
                },
            }

            if payment_method == "pix":
                payment_data["payment_method_id"] = "pix"
            elif payment_method == "credit_card":
                payment_data["token"] = kwargs.get("card_token")
                payment_data["installments"] = kwargs.get("installments", 1)
                payment_data["payment_method_id"] = kwargs.get("payment_method_id")
            elif payment_method == "boleto":
                payment_data["payment_method_id"] = "bolbradesco"

            result = self.sdk.payment().create(payment_data)

            if result["status"] == 201:
                response = result["response"]
                return PaymentResult(
                    success=True,
                    payment_id=str(response["id"]),
                    status=self._map_status(response["status"]),
                    message="Payment created successfully",
                    data={
                        "gateway_status": response["status"],
                        "pix_qr_code": response.get("point_of_interaction", {})
                        .get("transaction_data", {})
                        .get("qr_code"),
                        "pix_qr_code_base64": response.get("point_of_interaction", {})
                        .get("transaction_data", {})
                        .get("qr_code_base64"),
                        "boleto_url": response.get("transaction_details", {}).get(
                            "external_resource_url"
                        ),
                        "boleto_barcode": response.get("barcode", {}).get("content"),
                    },
                )
            else:
                return PaymentResult(
                    success=False,
                    status="rejected",
                    message=result.get("message", "Payment creation failed"),
                    error=str(result),
                )

        except Exception as e:
            logger.exception("Mercado Pago payment error")
            return PaymentResult(
                success=False,
                status="error",
                message="Payment processing error",
                error=str(e),
            )

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Mercado Pago."""
        try:
            result = self.sdk.payment().get(payment_id)
            if result["status"] == 200:
                response = result["response"]
                return {
                    "id": response["id"],
                    "status": self._map_status(response["status"]),
                    "gateway_status": response["status"],
                    "amount": Decimal(str(response["transaction_amount"])),
                    "fee": Decimal(
                        str(response.get("fee_details", [{}])[0].get("amount", 0))
                    ),
                }
            return {"error": "Payment not found"}
        except Exception as e:
            logger.exception("Mercado Pago status check error")
            return {"error": str(e)}

    def process_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process Mercado Pago webhook."""
        try:
            action = payload.get("action")
            data = payload.get("data", {})
            payment_id = data.get("id")

            if action == "payment.updated" and payment_id:
                return self.get_payment_status(str(payment_id))

            return {"action": action, "data": data}
        except Exception as e:
            logger.exception("Mercado Pago webhook error")
            return {"error": str(e)}

    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "",
    ) -> RefundResult:
        """Refund a payment on Mercado Pago."""
        try:
            refund_data = {}
            if amount:
                refund_data["amount"] = float(amount)

            result = self.sdk.refund().create(payment_id, refund_data)

            if result["status"] == 201:
                response = result["response"]
                return RefundResult(
                    success=True,
                    refund_id=str(response["id"]),
                    status="approved",
                    message="Refund processed successfully",
                )
            else:
                return RefundResult(
                    success=False,
                    status="rejected",
                    message="Refund failed",
                    error=str(result),
                )

        except Exception as e:
            logger.exception("Mercado Pago refund error")
            return RefundResult(
                success=False,
                status="error",
                message="Refund processing error",
                error=str(e),
            )

    def _map_status(self, gateway_status: str) -> str:
        """Map Mercado Pago status to internal status."""
        status_map = {
            "pending": "pending",
            "approved": "approved",
            "authorized": "processing",
            "in_process": "processing",
            "in_mediation": "processing",
            "rejected": "rejected",
            "cancelled": "cancelled",
            "refunded": "refunded",
            "charged_back": "refunded",
        }
        return status_map.get(gateway_status, "pending")
