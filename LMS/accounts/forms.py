from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import User
from management_system.models import RenewalRequest


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
                   "phone_number"
                   )

        labels = {
            "password1": "Password",
            "password2": "Password Confirmation"
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
                   "email", "password1", "password2", "username"
                   )


class RenewalRequestForm(forms.ModelForm):
    class Meta:
        model = RenewalRequest
        fields = ("renewal_days",)


class WalletPinForm(forms.Form):
    pin = forms.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
