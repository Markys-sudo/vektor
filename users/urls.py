from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, OrderHistoryView
from django.urls import include

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("orders/", OrderHistoryView.as_view(), name="order_history"),
    
]