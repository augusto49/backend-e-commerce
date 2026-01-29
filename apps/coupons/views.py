"""
Views for the coupons app.
Views para o app de cupons.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import InvalidCouponException
from apps.core.permissions import IsAdminUser

from .models import Coupon
from .serializers import CouponAdminSerializer, CouponSerializer, CouponValidateSerializer



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


class CouponAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for coupon management.
    ViewSet administrativo para gestão de cupons.
    """

    permission_classes = [IsAdminUser]
    queryset = Coupon.objects.all().order_by("-created_at")
    serializer_class = CouponAdminSerializer
    filterset_fields = ["is_active", "discount_type", "first_purchase_only"]
    search_fields = ["code", "description"]
    ordering_fields = ["created_at", "valid_from", "valid_until", "times_used"]

    @action(detail=True, methods=["get"])
    def usages(self, request, pk=None):
        """
        Get usage history for a coupon.
        Obtém histórico de uso de um cupom.
        """
        coupon = self.get_object()
        usages = coupon.usages.select_related("user", "order").order_by("-created_at")[:50]
        data = [
            {
                "id": u.id,
                "user_email": u.user.email,
                "order_number": u.order.number if u.order else None,
                "used_at": u.created_at,
            }
            for u in usages
        ]
        return Response({"success": True, "data": data})

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle coupon active status.
        Alterna status ativo do cupom.
        """
        coupon = self.get_object()
        coupon.is_active = not coupon.is_active
        coupon.save()
        return Response(
            {
                "success": True,
                "message": f"Coupon {'activated' if coupon.is_active else 'deactivated'}.",
                "data": CouponAdminSerializer(coupon).data,
            }
        )
