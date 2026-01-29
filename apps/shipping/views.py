"""
Shipping calculation views.
"""

import logging
from decimal import Decimal

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import ShippingCalculationException

from .services import CorreiosService

logger = logging.getLogger(__name__)


class CalculateShippingView(APIView):
    """
    Calculate shipping cost using Correios API.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        zipcode = request.data.get("zipcode", "").replace("-", "").replace(".", "")
        weight = Decimal(str(request.data.get("weight", 0.5)))
        
        # Package dimensions (optional)
        length = int(request.data.get("length", 20))
        height = int(request.data.get("height", 10))
        width = int(request.data.get("width", 15))

        if not zipcode or len(zipcode) != 8:
            raise ShippingCalculationException("Invalid ZIP code.")

        try:
            service = CorreiosService()
            options = service.calculate_shipping(
                destination_cep=zipcode,
                weight=weight,
                length=length,
                height=height,
                width=width,
            )

            # Convert to dict for JSON response
            result = [
                {
                    "code": opt.code,
                    "name": opt.name,
                    "price": str(opt.price),
                    "delivery_time": opt.delivery_time,
                    "min_days": opt.min_days,
                    "max_days": opt.max_days,
                    "error": opt.error,
                }
                for opt in options
                if not opt.error  # Filter out options with errors
            ]

            return Response({"success": True, "data": result})

        except Exception as e:
            logger.exception("Shipping calculation error")
            raise ShippingCalculationException(str(e))


class TrackShipmentView(APIView):
    """
    Track a shipment using Correios tracking.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, tracking_code):
        if not tracking_code or len(tracking_code) < 10:
            return Response(
                {"success": False, "message": "Invalid tracking code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = CorreiosService()
            tracking_info = service.track_package(tracking_code)

            if tracking_info.get("error"):
                return Response(
                    {
                        "success": False,
                        "message": tracking_info["error"],
                        "data": tracking_info,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({"success": True, "data": tracking_info})

        except Exception as e:
            logger.exception("Tracking error")
            return Response(
                {"success": False, "message": "Could not track shipment."},
                status=status.HTTP_400_BAD_REQUEST,
            )
