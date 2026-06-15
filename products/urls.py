from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductListView, ProductDetailView, ProductViewSet

app_name = "products"

router = DefaultRouter()
router.register(r"api/products", ProductViewSet, basename="products")

urlpatterns = [
    # Django pages
    path("", ProductListView.as_view(), name="product_list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),

    # API
    path("", include(router.urls)),
]