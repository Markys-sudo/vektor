from django.urls import path
from .views import RegisterView, LoginView, LogoutView, OrderHistoryView, AccountInfoView
from django.urls import include

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("orders/", OrderHistoryView.as_view(), name="order_history"),
    path("account-info/", AccountInfoView.as_view(), name="account_info"),
]