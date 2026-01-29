"""
Views for the wishlist app.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product

from .models import WishlistItem
from .serializers import WishlistAddSerializer, WishlistItemSerializer


class WishlistView(APIView):
    """
    Get user's wishlist.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = WishlistItem.objects.filter(user=request.user).select_related("product")
        serializer = WishlistItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})


class WishlistAddView(APIView):
    """
    Add item to wishlist.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WishlistAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(
                id=serializer.validated_data["product_id"],
                is_active=True,
            )
        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product,
        )

        if created:
            message = "Product added to wishlist."
        else:
            message = "Product is already in wishlist."

        return Response(
            {
                "success": True,
                "message": message,
                "data": WishlistItemSerializer(item).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class WishlistRemoveView(APIView):
    """
    Remove item from wishlist.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        try:
            item = WishlistItem.objects.get(
                user=request.user,
                product_id=product_id,
            )
            item.delete()
            return Response(
                {"success": True, "message": "Product removed from wishlist."}
            )
        except WishlistItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Product not in wishlist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class WishlistCheckView(APIView):
    """
    Check if product is in wishlist.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            product_id=product_id,
        ).exists()
        return Response({"success": True, "in_wishlist": in_wishlist})
