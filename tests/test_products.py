"""
Tests for the products app.
"""

import pytest
from decimal import Decimal
from rest_framework import status


@pytest.mark.django_db
class TestProductList:
    """Tests for product list endpoint."""

    def test_list_products_empty(self, api_client):
        """Test listing products when none exist."""
        response = api_client.get("/api/v1/products/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_list_products_with_data(self, api_client, product):
        """Test listing products with data."""
        response = api_client.get("/api/v1/products/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        results = response.data.get("data", {}).get("results", response.data.get("results", []))
        assert len(results) >= 1

    def test_list_products_filter_by_category(self, api_client, product, category):
        """Test filtering products by category."""
        response = api_client.get(f"/api/v1/products/?category={category.slug}")
        
        assert response.status_code == status.HTTP_200_OK

    def test_list_products_search(self, api_client, product):
        """Test searching products."""
        response = api_client.get("/api/v1/products/?search=iPhone")
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductDetail:
    """Tests for product detail endpoint."""

    def test_get_product_by_slug(self, api_client, product):
        """Test getting product by slug."""
        response = api_client.get(f"/api/v1/products/{product.slug}/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data.get("data", response.data)
        assert data["name"] == product.name

    def test_get_product_not_found(self, api_client):
        """Test getting non-existent product."""
        response = api_client.get("/api/v1/products/nonexistent-product/")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategories:
    """Tests for category endpoints."""

    def test_list_categories(self, api_client, category):
        """Test listing categories."""
        response = api_client.get("/api/v1/products/categories/")
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductReviews:
    """Tests for product reviews."""

    def test_create_review_unauthenticated(self, api_client, product):
        """Test creating a review when not authenticated."""
        data = {
            "rating": 5,
            "title": "Great product!",
            "comment": "Love this phone.",
        }
        response = api_client.post(
            f"/api/v1/products/{product.slug}/reviews/", data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_product_reviews(self, api_client, product):
        """Test listing product reviews."""
        response = api_client.get(f"/api/v1/products/{product.slug}/reviews/")
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductModel:
    """Tests for Product model."""

    def test_product_current_price_with_sale(self, product):
        """Test current_price returns sale_price when available."""
        product.sale_price = Decimal("4999.90")
        product.save()
        
        assert product.current_price == Decimal("4999.90")

    def test_product_current_price_no_sale(self, db):
        """Test current_price returns base_price when no sale."""
        from apps.products.models import Product, Category, Brand
        
        cat = Category.objects.create(name="Test", slug="test")
        brand = Brand.objects.create(name="Test Brand", slug="test-brand")
        
        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            category=cat,
            brand=brand,
            base_price=Decimal("100.00"),
            sale_price=None,
        )
        
        assert product.current_price == Decimal("100.00")

    def test_product_str(self, product):
        """Test product string representation."""
        assert str(product) == product.name


@pytest.mark.django_db
class TestStockModel:
    """Tests for Stock model."""

    def test_stock_available_quantity(self, product_with_stock):
        """Test available quantity calculation."""
        from apps.products.models import Stock
        
        stock = Stock.objects.get(product=product_with_stock)
        stock.reserved_quantity = 10
        stock.save()
        
        assert stock.available_quantity == 90

    def test_stock_is_low(self, product_with_stock):
        """Test low stock check."""
        from apps.products.models import Stock
        
        stock = Stock.objects.get(product=product_with_stock)
        stock.quantity = 5  # Below threshold of 10
        stock.save()
        
        assert stock.is_low_stock is True
