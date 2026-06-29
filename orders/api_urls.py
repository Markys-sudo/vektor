from rest_framework.routers import DefaultRouter
from .api_views import CartViewSet
from .api import OrderViewSet

# 1. Ініціалізуємо роутер та реєструємо ViewSet
router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")
router.register("cart", CartViewSet, basename="api_cart")
# 2. Створюємо список ручних маршрутів


# 3. Додаємо (об'єднуємо) маршрути роутера до загального списку
urlpatterns = router.urls
