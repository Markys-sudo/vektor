from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django import forms
from .models import User
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        placeholders = {
            "username": "Username",
            "email": "Email",
            "password1": "Password",
            "password2": "Confirm Password",
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs.update(
                {"class": "Input", "placeholder": placeholder}
            )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "Input", "placeholder": "Username or Email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "Input", "placeholder": "Password"}
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError(
                    "Invalid username/email or password. Please try again."
                )
            self.user = user  # Store the authenticated user for later use
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "email", "city", "address"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "Input", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "Input", "placeholder": "Last Name"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "Input", "placeholder": "Phone Number"}
            ),
            "email": forms.EmailInput(attrs={"class": "Input", "placeholder": "Email"}),
            "city": forms.TextInput(attrs={"class": "Input", "placeholder": "City"}),
            "address": forms.Textarea(
                attrs={"class": "Textarea", "placeholder": "Address", "rows": 3}
            ),
        }


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update(
            {"class": "Input", "placeholder": "Old Password"}
        )
        self.fields["new_password1"].widget.attrs.update(
            {"class": "Input", "placeholder": "New Password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "Input", "placeholder": "Confirm New Password"}
        )


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "Input", "placeholder": "Enter your email"}
        )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс 'Input' и плейсхолдеры для обоих полей
        self.fields["new_password1"].widget.attrs.update(
            {"class": "Input", "placeholder": "New password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "Input", "placeholder": "Confirm new password"}
        )
