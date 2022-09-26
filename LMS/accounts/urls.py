from django.urls import path

from .views import (sign_up,
                    sign_in,
                    UserInboxView,
                    UserBorrowedBooksView,
                    sign_out,
                    wallet_view,
                    books_calendar_view,
                    make_renewal_request
                    )

app_name = "accounts"

urlpatterns = [
    path("sign-up/", sign_up, name="sign_up"),
    path("sign-in/", sign_in, name="sign_in"),
    path("sign-out/", sign_out, name="sign_out"),
    path("inbox/", UserInboxView.as_view(), name="user_inbox"),
    path("borrowed_books/", UserBorrowedBooksView.as_view(), name="user_borrowed_books"),
    path("wallet/", wallet_view, name="user_wallet"),
    path("book_calendar/", books_calendar_view, name="books_calendar"),
    path("make_renewal_request/<int:pk>", make_renewal_request, name="make_renewal"),

]
