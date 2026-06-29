"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from products.views import ProductListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", ProductListView.as_view(), name="home"),
    path("", include("products.urls", namespace="products")),
    path("accounts/", include("users.urls")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"
    ),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/auth/", include("users.api_urls")),  # Authentication API
    path("api/", include("products.api_urls")),  # API
    path("api/", include("orders.api_urls")),  # API
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
