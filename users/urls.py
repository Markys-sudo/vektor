from django.urls import path

from users.forms import CustomPasswordResetForm, CustomSetPasswordForm
from .views import RegisterView, LoginView, LogoutView, OrderHistoryView, AccountInfoView, ChangePasswordView
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("orders/", OrderHistoryView.as_view(), name="order_history"),
    path("account-info/", AccountInfoView.as_view(), name="account_info"),
    
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name="password_reset_done"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html",
            email_template_name="auth/password_reset_email.html",   
            form_class=CustomPasswordResetForm,
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),

    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url="/accounts/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),

]