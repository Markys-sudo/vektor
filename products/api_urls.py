from rest_framework.routers import DefaultRouter
from .api_view import ProductViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"categories", CategoryViewSet, basename="categories")

urlpatterns = router.urls