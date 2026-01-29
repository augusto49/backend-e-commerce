"""
Base payment gateway interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class PaymentResult:
    """Result of a payment operation."""

    success: bool
    payment_id: Optional[str] = None
    status: str = "pending"
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class RefundResult:
    """Result of a refund operation."""

    success: bool
    refund_id: Optional[str] = None
    status: str = "pending"
    message: str = ""
    error: Optional[str] = None


class BasePaymentGateway(ABC):
    """
    Abstract base class for payment gateways.
    """

    @abstractmethod
    def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_method: str,
        customer_data: Dict[str, Any],
        **kwargs,
    ) -> PaymentResult:
        """
        Create a payment.

        Args:
            order_id: Order ID
            amount: Payment amount
            payment_method: Payment method (credit_card, pix, boleto)
            customer_data: Customer information
            **kwargs: Additional gateway-specific parameters

        Returns:
            PaymentResult with payment information
        """
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status from gateway.

        Args:
            payment_id: Gateway payment ID

        Returns:
            Dictionary with payment status and details
        """
        pass

    @abstractmethod
    def process_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process webhook notification from gateway.

        Args:
            payload: Webhook payload
            signature: Webhook signature for verification

        Returns:
            Processed webhook data
        """
        pass

    @abstractmethod
    def refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "",
    ) -> RefundResult:
        """
        Refund a payment.

        Args:
            payment_id: Gateway payment ID
            amount: Amount to refund (None for full refund)
            reason: Refund reason

        Returns:
            RefundResult with refund information
        """
        pass

    def _format_amount(self, amount: Decimal) -> int:
        """Convert decimal amount to cents (integer)."""
        return int(amount * 100)

    def _parse_amount(self, amount_cents: int) -> Decimal:
        """Convert cents to decimal amount."""
        return Decimal(amount_cents) / 100
