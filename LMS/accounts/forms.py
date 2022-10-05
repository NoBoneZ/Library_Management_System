from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Members
from management_system.models import RenewalRequest


class CustomMembersCreationForm(UserCreationForm):
    class Meta:
        model = Members
        exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
                   "phone_number"
                   )

        labels = {
            "password1": "Password",
            "password2": "Password Confirmation"
        }



class CustomMembersChangeForm(UserChangeForm):
    class Meta:
        model = Members
        # exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
        #            "email", "password1", "password2", "username"
        #            # )
        fields = ["first_name", "last_name", "middle_name", "profile_picture",
                  "phone_number", "age", "gender", "address"
                  ]


class RenewalRequestForm(forms.ModelForm):
    class Meta:
        model = RenewalRequest
        fields = ("renewal_days",)


class WalletPinForm(forms.Form):
    pin = forms.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
