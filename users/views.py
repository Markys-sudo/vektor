from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View

from .models import User

class RegisterView(View):
    def get(self, request):
        return render(request, "auth/register.html")

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect("accounts:register")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("accounts:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("accounts:register")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(request, "Account created successfully")
        return redirect("home")
    
    
class LoginView(View):
    def get(self, request):
        return render(request, "auth/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 1. try login by username
        user = authenticate(request, username=username, password=password)

        # 2. fallback: treat input as email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)

                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid credentials")
        return redirect("accounts:login")
    
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:login")
    
    
class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        
        return render(request, "auth/profile.html", {"user": request.user})
    