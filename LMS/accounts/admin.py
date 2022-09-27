from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomMembersChangeForm
from .models import Members, Wallet, Inbox, WalletTransaction


class CustomMembersAdmin(UserAdmin):
    class Meta:
        form = CustomMembersChangeForm

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


class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_type", "amount", "date_occurred", "balance")
    list_filter = ("wallet",)


# Register your models here.

admin.site.register(Members, CustomMembersAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Inbox, InboxAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)
