from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .models import User, Wallet, Inbox


class CustomUserAdmin(UserAdmin):
    class Meta:
        form = CustomUserChangeForm

        fieldsets = (('Main Information',
                      {"fields": (
                          "first_name", "middle_name", "last_name", "profile_picture", "username", "phone_number")}),
                     ("addresses", {"fields": ("email", "address")}),
                     ("others", {"fields": ("age", "last_login",)})
                     )

        list_display = ["first_name", "last_name", "email", "username"]
        ordering = ["first_name"]


class WalletAdmin(admin.ModelAdmin):
    list_display = ("owner", "wallet_number", "outstanding_debts", "balance")


class InboxAdmin(admin.ModelAdmin):
    list_display = ("sender", "date_created", "is_read")


# Register your models here.

admin.site.register(User, CustomUserAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Inbox, InboxAdmin)
