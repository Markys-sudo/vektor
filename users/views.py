from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from orders.models import Order
from .models import User, UserProfile
from .filters import OrderFilter
from .forms import RegisterForm, LoginForm, UserProfileForm
from django_filters.views import FilterView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy


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
    
    
class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "auth/change_password.html")

    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("accounts:change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("accounts:change_password")

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, "Password changed successfully. Please log in again.")
        logout(request)
        return redirect("accounts:login")