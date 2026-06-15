from rest_framework import viewsets

from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Public, read-only catalog API. Reuses the web ProductFilter."""

    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        return (
            Product.objects.active()
            .with_rating()
            .with_popularity()
            .select_related("category")
            .order_by("-created_at")
        )
