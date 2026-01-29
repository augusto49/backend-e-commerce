"""
Filters for the products app.
"""

from django_filters import rest_framework as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    """
    Filter for products.
    """

    min_price = filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="base_price", lookup_expr="lte")
    category = filters.CharFilter(field_name="category__slug")
    brand = filters.CharFilter(field_name="brand__slug")
    on_sale = filters.BooleanFilter(method="filter_on_sale")
    in_stock = filters.BooleanFilter(method="filter_in_stock")
    featured = filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "min_price",
            "max_price",
            "on_sale",
            "in_stock",
            "featured",
        ]

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(
                sale_price__isnull=False,
                sale_price__lt=models.F("base_price"),
            )
        return queryset

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                stock_items__quantity__gt=models.F("stock_items__reserved_quantity")
            ).distinct()
        return queryset
