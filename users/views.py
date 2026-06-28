from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order
from django.contrib.auth import get_user_model
from .filters import OrderFilter
from .forms import RegisterForm, LoginForm, UserProfileForm, CustomPasswordChangeForm, UserProfileForm
from django_filters.views import FilterView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.views.generic.edit import FormView
from orders.cart import Cart


User = get_user_model()

class OrderHistoryView(LoginRequiredMixin, FilterView):
    template_name = "users/order_history.html"
    model = Order
    filterset_class = OrderFilter
    paginate_by = 7
    context_object_name = "orders"  # Переменная списка в шаблоне


    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .order_by("-created_at")
            .prefetch_related("items__product")
        )
    
    
class AccountInfoView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/account_info.html"
    success_url = reverse_lazy("accounts:account_info")

    def get_object(self, queryset=None):
        return self.request.user


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "auth/register.html", {"form": form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("home")
        return render(request, "auth/register.html", {"form": form})
    
    
class LoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "auth/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            # 1. Сохраняем товары гостя во временную переменную до очистки сессии
            session_cart_data = request.session.get("cart", {})
            # беремо user з форми
            login(request, form.user)
            if session_cart_data:
                request.session["cart"] = session_cart_data
                cart = Cart(request)
                cart.merge_session_cart()
            messages.success(request, "Welcome back!")
            return redirect("home")
        return render(request, "auth/login.html", {"form": form})
    
    
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:login")
    
    
class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = "auth/change_password.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("accounts:login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Сохраняем новый пароль
        user = form.save()
                # Обновляем сессию, чтобы пользователя не выбросило из системы (опционально)
        update_session_auth_hash(self.request, user)
        
        messages.success(self.request, "Password changed successfully.")
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/account_info.html"
    success_url = reverse_lazy("accounts:account_info")

    def get_object(self, queryset=None):
        return self.request.user