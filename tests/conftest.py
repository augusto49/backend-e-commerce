"""
Pytest configuration and fixtures for E-commerce Backend tests.
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()



@pytest.fixture(autouse=True)
def disable_throttling(settings):
    """Disable throttling and Axes for all tests."""
    settings.AXES_ENABLED = False
    settings.REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        # Remove throttling
    }

@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a regular user."""
    return User.objects.create_user(
        email="testuser@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        is_verified=True,
    )


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="AdminPass123!",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an admin authenticated API client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def category(db):
    """Create and return a category."""
    from apps.products.models import Category
    return Category.objects.create(
        name="Electronics",
        slug="electronics",
        is_active=True,
    )


@pytest.fixture
def brand(db):
    """Create and return a brand."""
    from apps.products.models import Brand
    return Brand.objects.create(
        name="Apple",
        slug="apple",
        is_active=True,
    )


@pytest.fixture
def product(db, category, brand):
    """Create and return a product."""
    from apps.products.models import Product
    return Product.objects.create(
        name="iPhone 15",
        slug="iphone-15",
        sku="IPH15-001",
        category=category,
        brand=brand,
        base_price=Decimal("5999.90"),
        sale_price=Decimal("5499.90"),
        is_active=True,
    )


@pytest.fixture
def product_with_stock(db, product):
    """Create and return a product with stock."""
    from apps.products.models import Stock
    Stock.objects.create(
        product=product,
        quantity=100,
        low_stock_threshold=10,
    )
    return product


@pytest.fixture
def cart(db, user):
    """Create and return a cart for the user."""
    from apps.cart.models import Cart
    return Cart.objects.create(user=user)


@pytest.fixture
def cart_with_items(db, cart, product_with_stock):
    """Create and return a cart with items."""
    from apps.cart.models import CartItem
    CartItem.objects.create(
        cart=cart,
        product=product_with_stock,
        quantity=2,
        unit_price=product_with_stock.current_price,
    )
    return cart


@pytest.fixture
def address(db, user):
    """Create and return an address for the user."""
    from apps.accounts.models import Address
    return Address.objects.create(
        user=user,
        name="Casa",
        recipient_name="Test User",
        street="Av. Paulista",
        number="1000",
        neighborhood="Bela Vista",
        city="São Paulo",
        state="SP",
        zipcode="01310100",
        is_default=True,
    )


@pytest.fixture
def coupon(db):
    """Create and return a valid coupon."""
    from apps.coupons.models import Coupon
    from django.utils import timezone
    from datetime import timedelta
    
    return Coupon.objects.create(
        code="DESCONTO10",
        description="10% off",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        min_order_value=Decimal("50.00"),
        is_active=True,
        valid_from=timezone.now() - timedelta(days=1),
        valid_until=timezone.now() + timedelta(days=30),
    )
