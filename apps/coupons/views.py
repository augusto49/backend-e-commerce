"""
Views for the coupons app.
Views para o app de cupons.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import InvalidCouponException

from .models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer


class CouponValidateView(APIView):
    """
    Validate a coupon code.
    Valida um código de cupom.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        order_value = serializer.validated_data.get("order_value", 0)

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            raise InvalidCouponException("Coupon not found.")

        can_use, error_message = coupon.can_use(request.user, order_value)

        if not can_use:
            raise InvalidCouponException(error_message)

        discount = coupon.calculate_discount(order_value) if order_value else None

        return Response(
            {
                "success": True,
                "message": "Coupon is valid.",
                "data": {
                    "coupon": CouponSerializer(coupon).data,
                    "discount": str(discount) if discount else None,
                },
            }
        )
