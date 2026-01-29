"""
Stripe payment gateway integration.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings

from .base import BasePaymentGateway, PaymentResult, RefundResult

logger = logging.getLogger(__name__)


class StripeGateway(BasePaymentGateway):
    """
    Stripe payment gateway.
    """

    def __init__(self):
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_method: str,
        customer_data: Dict[str, Any],
        **kwargs,
    ) -> PaymentResult:
        """Create a payment with Stripe."""
        try:
            # Create or get customer
            customer = self._get_or_create_customer(customer_data)

            # Create payment intent
            intent = self.stripe.PaymentIntent.create(
                amount=self._format_amount(amount),
                currency="brl",
                customer=customer.id,
                payment_method=kwargs.get("payment_method_id"),
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never",
                },
                metadata={
                    "order_id": str(order_id),
                },
            )

            return PaymentResult(
                success=True,
                payment_id=intent.id,
                status=self._map_status(intent.status),
                message="Payment created successfully",
                data={
                    "client_secret": intent.client_secret,
                    "gateway_status": intent.status,
                },
            )

        except self.stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                status="rejected",
                message=str(e.user_message),
                error=str(e),
            )
        except Exception as e:
            logger.exception("Stripe payment error")
            return PaymentResult(
                success=False,
                status="error",
                message="Payment processing error",
                error=str(e),
            )

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Stripe."""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_id)
            return {
                "id": intent.id,
                "status": self._map_status(intent.status),
                "gateway_status": intent.status,
                "amount": self._parse_amount(intent.amount),
            }
        except Exception as e:
            logger.exception("Stripe status check error")
            return {"error": str(e)}

    def process_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process Stripe webhook."""
        try:
            event = self.stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )

            if event["type"] == "payment_intent.succeeded":
                intent = event["data"]["object"]
                return {
                    "id": intent["id"],
                    "status": "approved",
                    "order_id": intent["metadata"].get("order_id"),
                }
            elif event["type"] == "payment_intent.payment_failed":
                intent = event["data"]["object"]
                return {
                    "id": intent["id"],
                    "status": "rejected",
                    "order_id": intent["metadata"].get("order_id"),
                    "error": intent.get("last_payment_error", {}).get("message"),
                }

            return {"type": event["type"]}

        except self.stripe.error.SignatureVerificationError as e:
            logger.error("Stripe webhook signature verification failed")
            return {"error": "Invalid signature"}
        except Exception as e:
            logger.exception("Stripe webhook error")
            return {"error": str(e)}

    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "",
    ) -> RefundResult:
        """Refund a payment on Stripe."""
        try:
            refund_data = {"payment_intent": payment_id}
            if amount:
                refund_data["amount"] = self._format_amount(amount)
            if reason:
                refund_data["reason"] = "requested_by_customer"

            refund = self.stripe.Refund.create(**refund_data)

            return RefundResult(
                success=True,
                refund_id=refund.id,
                status="approved" if refund.status == "succeeded" else "pending",
                message="Refund processed successfully",
            )

        except Exception as e:
            logger.exception("Stripe refund error")
            return RefundResult(
                success=False,
                status="error",
                message="Refund processing error",
                error=str(e),
            )

    def _get_or_create_customer(self, customer_data: Dict[str, Any]):
        """Get or create a Stripe customer."""
        # Search for existing customer
        customers = self.stripe.Customer.list(email=customer_data.get("email"), limit=1)

        if customers.data:
            return customers.data[0]

        # Create new customer
        return self.stripe.Customer.create(
            email=customer_data.get("email"),
            name=f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
        )

    def _map_status(self, gateway_status: str) -> str:
        """Map Stripe status to internal status."""
        status_map = {
            "requires_payment_method": "pending",
            "requires_confirmation": "pending",
            "requires_action": "pending",
            "processing": "processing",
            "requires_capture": "processing",
            "succeeded": "approved",
            "canceled": "cancelled",
        }
        return status_map.get(gateway_status, "pending")
