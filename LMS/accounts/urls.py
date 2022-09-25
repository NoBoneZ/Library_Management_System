from django.urls import path

from .views import (sign_up,
                    sign_in,
                    UserInboxView,
                    UserBorrowedBooksView,
                    sign_out,
                    wallet_view
                    )

app_name = "accounts"

urlpatterns = [
    path("sign-up/", sign_up, name="sign_up"),
    path("sign-in/", sign_in, name="sign_in"),
    path("sign-out/", sign_out, name="sign_out"),
    path("inbox/", UserInboxView.as_view(), name="user_inbox"),
    path("borrowed_books/", UserBorrowedBooksView.as_view(), name="user_borrowed_books"),
    path("wallet/", wallet_view, name="user_wallet")

]
