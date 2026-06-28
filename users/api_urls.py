from django.urls import path
from .api_views import RegisterView, MeView, MeOrderView
from .api_tg import TelegramLinkAPIView, TelegramConfirmAPIView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("me/orders/", MeOrderView.as_view(), name="me-orders"),
    path("telegram-link/", TelegramLinkAPIView.as_view(), name="api_tg_link"),
    path("telegram/confirm/", TelegramConfirmAPIView.as_view(), name="api_tg_confirm"),

]

