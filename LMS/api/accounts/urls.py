from django.urls import path

from .views import (MemberListCreateView, AccountsApiRoot,
                    WalletListCreateView
                    )


app_name = "accounts_api"

urlpatterns = [
    path("", AccountsApiRoot.as_view(), name="accounts_root"),
    path("members", MemberListCreateView.as_view(), name="members_list_create"),


    path("wallet", WalletListCreateView.as_view(), name="wallet_list_create")
]
