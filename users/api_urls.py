from django.urls import path
from django.contrib.auth import views as auth_views
from .api_views import RegisterView, MeView, MeOrderView, UpdateUserPasswordView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("me/orders/", MeOrderView.as_view(), name="me-orders"),
    path("change-password/", UpdateUserPasswordView.as_view(), name="change-password"),
]

