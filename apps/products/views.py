"""
Views for the products app.
Views para o app de produtos.
"""

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.pagination import LargeResultsSetPagination
from apps.core.permissions import IsAdminUser

from .filters import ProductFilter
from .models import Brand, Category, Product, ProductReview, ProductVariation, Stock
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    CategoryTreeSerializer,
    ProductAdminSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductReviewCreateSerializer,
    ProductReviewSerializer,
    ProductVariationSerializer,
    StockSerializer,
    StockUpdateSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for product categories.
    ViewSet para categorias de produtos.
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "tree":
            return CategoryTreeSerializer
        return CategorySerializer

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Get category tree starting from root.
        Obtém a árvore de categorias a partir da raiz.
        """
        root_categories = Category.objects.filter(
            parent=None,
            is_active=True,
        ).order_by("order", "name")
        serializer = self.get_serializer(root_categories, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        """
        Get products in a category and its descendants.
        Obtém produtos em uma categoria e seus descendentes.
        """
        category = self.get_object()
        descendants = category.get_descendants(include_self=True)
        products = Product.objects.filter(
            category__in=descendants,
            is_active=True,
        ).order_by("-created_at")

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response({"success": True, "data": serializer.data})


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for product brands.
    ViewSet para marcas de produtos.
    """

    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for products.
    ViewSet para produtos.
    """

    queryset = Product.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    pagination_class = LargeResultsSetPagination
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["name", "base_price", "created_at", "order_count"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Get product detail and increment view count.
        Obtém detalhes do produto e incrementa contagem de visualizações.
        """
        instance = self.get_object()

        # Increment view count
        # Incrementa contagem de visualizações
        Product.objects.filter(pk=instance.pk).update(
            view_count=instance.view_count + 1
        )

        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """
        Get featured products.
        Obtém produtos em destaque.
        """
        products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def on_sale(self, request):
        """
        Get products on sale.
        Obtém produtos em promoção.
        """
        products = self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price__lt=models.F("base_price"),
        )
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=False, methods=["get"])
    def best_sellers(self, request):
        """
        Get best selling products.
        Obtém produtos mais vendidos.
        """
        products = self.get_queryset().order_by("-order_count")[:12]
        serializer = ProductListSerializer(products, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=True, methods=["get"])
    def reviews(self, request, slug=None):
        """
        Get product reviews.
        Obtém avaliações de produtos.
        """
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True).order_by("-created_at")

        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductReviewSerializer(reviews, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_review(self, request, slug=None):
        """
        Add a review to a product.
        Adiciona uma avaliação a um produto.
        """
        product = self.get_object()

        # Check if user already reviewed
        # Verifica se o usuário já avaliou
        if product.reviews.filter(user=request.user).exists():
            return Response(
                {
                    "success": False,
                    "message": "You have already reviewed this product.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProductReviewCreateSerializer(
            data=request.data,
            context={"request": request, "product": product},
        )
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Review submitted for moderation.",
                "data": ProductReviewSerializer(review).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def related(self, request, slug=None):
        """
        Get related products.
        Obtém produtos relacionados.
        """
        product = self.get_object()
        related = (
            Product.objects.filter(
                category=product.category,
                is_active=True,
            )
            .exclude(pk=product.pk)
            .order_by("?")[:6]
        )
        serializer = ProductListSerializer(related, many=True)
        return Response({"success": True, "data": serializer.data})


# Admin ViewSets
class ProductAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for product management.
    ViewSet de admin para gerenciamento de produtos.
    """

    queryset = Product.all_objects.all()
    serializer_class = ProductAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "sku"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """
        Export products to CSV.
        Exporta produtos para CSV.
        """
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["ID", "SKU", "Name", "Category", "Brand", "Price", "Stock", "Active"]
        )

        products = self.filter_queryset(self.get_queryset())
        for product in products:
            writer.writerow(
                [
                    product.id,
                    product.sku,
                    product.name,
                    product.category.name if product.category else "",
                    product.brand.name if product.brand else "",
                    product.base_price,
                    product.total_stock,
                    product.is_active,
                ]
            )

        return response


class StockAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for stock management.
    ViewSet de admin para gerenciamento de estoque.
    """

    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["patch"])
    def update_quantity(self, request, pk=None):
        """
        Update stock quantity.
        Atualiza quantidade de estoque.
        """
        stock = self.get_object()
        serializer = StockUpdateSerializer(
            stock,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(stock, serializer.validated_data)

        return Response(
            {
                "success": True,
                "message": "Stock updated successfully.",
                "data": StockSerializer(stock).data,
            }
        )

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """
        Get products with low stock.
        Obtém produtos com estoque baixo.
        """
        low_stock = Stock.objects.filter(
            quantity__lte=models.F("low_stock_threshold")
        ).select_related("product", "variation")

        serializer = self.get_serializer(low_stock, many=True)
        return Response({"success": True, "data": serializer.data})


class CategoryAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for category management.
    ViewSet de admin para gerenciamento de categorias.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering = ["order", "name"]

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Get category tree for admin.
        Obtém árvore de categorias para admin.
        """
        root_categories = Category.objects.filter(parent=None)
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response({"success": True, "data": serializer.data})

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle category active status.
        Alterna status ativo da categoria.
        """
        category = self.get_object()
        category.is_active = not category.is_active
        category.save()
        return Response(
            {
                "success": True,
                "message": f"Category {'activated' if category.is_active else 'deactivated'}.",
                "data": CategorySerializer(category).data,
            }
        )


class BrandAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for brand management.
    ViewSet de admin para gerenciamento de marcas.
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering = ["name"]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle brand active status.
        Alterna status ativo da marca.
        """
        brand = self.get_object()
        brand.is_active = not brand.is_active
        brand.save()
        return Response(
            {
                "success": True,
                "message": f"Brand {'activated' if brand.is_active else 'deactivated'}.",
                "data": BrandSerializer(brand).data,
            }
        )

