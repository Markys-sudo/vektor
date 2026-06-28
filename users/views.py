from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order
from .models import UserProfile
from .filters import OrderFilter
from .forms import RegisterForm, LoginForm, UserProfileForm, CustomPasswordChangeForm
from django_filters.views import FilterView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import FormView


class OrderHistoryView(LoginRequiredMixin, FilterView):
    template_name = "users/order_history.html"
    model = Order
    filterset_class = OrderFilter
    context_object_name = "orders"
    paginate_by = 7

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .order_by("-created_at")
            .prefetch_related("items__product")
        )
    
    
class AccountInfoView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "users/account_info.html"
    success_url = reverse_lazy("accounts:account_info")

    def get_object(self, queryset=None):
        # Get or create the UserProfile for the logged-in user
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


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
            # беремо user з форми
            login(request, form.user)
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