from django.urls import path
from .api_views import RegisterView, MeView, MeOrderView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("me/orders/", MeOrderView.as_view(), name="me-orders"),
]

