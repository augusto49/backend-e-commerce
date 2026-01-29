"""
Custom exception handlers for the E-commerce API.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response_data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": get_error_message(exc),
                "details": response.data,
            },
        }
        response.data = custom_response_data

    return response


def get_error_message(exc):
    """Get a human-readable error message from an exception."""
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, str):
            return exc.detail
        elif isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else "An error occurred"
        elif isinstance(exc.detail, dict):
            # Get the first error message from the dict
            for key, value in exc.detail.items():
                if isinstance(value, list):
                    return f"{key}: {value[0]}"
                return f"{key}: {value}"
    return str(exc)


class BusinessLogicException(APIException):
    """
    Exception for business logic errors.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A business logic error occurred."
    default_code = "business_error"


class InsufficientStockException(BusinessLogicException):
    """
    Exception raised when there's not enough stock for a product.
    """

    default_detail = "Insufficient stock for this product."
    default_code = "insufficient_stock"


class CartEmptyException(BusinessLogicException):
    """
    Exception raised when trying to checkout with an empty cart.
    """

    default_detail = "Cart is empty."
    default_code = "cart_empty"


class OrderAlreadyPaidException(BusinessLogicException):
    """
    Exception raised when trying to pay for an already paid order.
    """

    default_detail = "This order has already been paid."
    default_code = "order_already_paid"


class InvalidCouponException(BusinessLogicException):
    """
    Exception raised when a coupon is invalid or expired.
    """

    default_detail = "This coupon is invalid or expired."
    default_code = "invalid_coupon"


class PaymentFailedException(BusinessLogicException):
    """
    Exception raised when a payment fails.
    """

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "Payment failed. Please try again."
    default_code = "payment_failed"


class ShippingCalculationException(BusinessLogicException):
    """
    Exception raised when shipping calculation fails.
    """

    default_detail = "Could not calculate shipping for this address."
    default_code = "shipping_calculation_failed"
