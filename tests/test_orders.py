"""
Tests for the orders app.
"""

import pytest
from decimal import Decimal
from rest_framework import status


@pytest.mark.django_db
class TestOrderList:
    """Tests for order list endpoint."""

    def test_list_orders_authenticated(self, authenticated_client):
        """Test listing orders when authenticated."""
        response = authenticated_client.get("/api/v1/orders/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_list_orders_unauthenticated(self, api_client):
        """Test listing orders when not authenticated."""
        response = api_client.get("/api/v1/orders/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCheckout:
    """Tests for checkout endpoint."""

    def test_checkout_unauthenticated(self, api_client):
        """Test checkout when not authenticated."""
        data = {}
        response = api_client.post("/api/v1/orders/checkout/", data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_checkout_empty_cart(self, authenticated_client, cart, address):
        """Test checkout with empty cart."""
        data = {
            "shipping_address_id": address.id,
            "billing_address_id": address.id,
            "shipping_method": "sedex",
        }
        response = authenticated_client.post("/api/v1/orders/checkout/", data)
        
        # Should fail with empty cart
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestOrderModel:
    """Tests for Order model."""

    def test_order_number_generation(self, db, user):
        """Test that order numbers are generated correctly."""
        from apps.orders.models import Order
        
        order = Order.objects.create(
            user=user,
            subtotal=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
            total=Decimal("110.00"),
        )
        
        assert order.number.startswith("ORD-")
        assert len(order.number) == 17  # ORD-YYYY-XXXXXXXX

    def test_order_status_default(self, db, user):
        """Test that order status defaults to pending."""
        from apps.orders.models import Order
        
        order = Order.objects.create(
            user=user,
            subtotal=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
            total=Decimal("110.00"),
        )
        
        assert order.status == "pending"

    def test_order_str(self, db, user):
        """Test order string representation."""
        from apps.orders.models import Order
        
        order = Order.objects.create(
            user=user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        
        assert order.number in str(order)


@pytest.mark.django_db
class TestOrderStatusHistory:
    """Tests for order status history."""

    def test_status_history_created(self, db, user):
        """Test that status history can be created."""
        from apps.orders.models import Order, OrderStatusHistory
        
        order = Order.objects.create(
            user=user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        
        # Create status history manually
        OrderStatusHistory.objects.create(
            order=order,
            status="paid",
            notes="Payment confirmed",
            created_by=user,
        )
        
        assert order.status_history.count() == 1
        assert order.status_history.first().status == "paid"


@pytest.mark.django_db
class TestOrderItemModel:
    """Tests for OrderItem model."""

    def test_order_item_str(self, db, user, product):
        """Test order item string representation."""
        from apps.orders.models import Order, OrderItem
        
        order = Order.objects.create(
            user=user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            quantity=2,
            unit_price=Decimal("50.00"),
            total_price=Decimal("100.00"),
        )
        
        assert product.name in str(item)
