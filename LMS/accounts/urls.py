from django.urls import path

from .views import (sign_up,
                    sign_in,
                    MembersInboxView,
                    MembersBorrowedBooksView,
                    sign_out,
                    wallet_view,
                    books_calendar_view,
                    make_renewal_request,
                    forgot_password,
                    reset_password,
                    profile_page_view,
                    transaction_report_csv,
                    credit_wallet
                    )

app_name = "accounts"

urlpatterns = [
    path("sign-up/", sign_up, name="sign_up"),
    path("sign-in/", sign_in, name="sign_in"),
    path("sign-out/", sign_out, name="sign_out"),
    path("forgot_password", forgot_password, name="forgot_password"),
    path('reset_password/password-token/<str:uid>/<str:token>', reset_password, name='reset_password'),
    path("profile_page/", profile_page_view, name="profile_page"),

    path("inbox/", MembersInboxView.as_view(), name="member_inbox"),
    path("books/", MembersBorrowedBooksView.as_view(), name="books"),
    path("wallet/", wallet_view, name="member_wallet"),
    path("book_calendar/", books_calendar_view, name="books_calendar"),
    path("make_renewal_request/<int:pk>", make_renewal_request, name="make_renewal"),

    path("transaction_report/", transaction_report_csv, name='transaction_report'),
    path("credit_wallet/", credit_wallet, name="credit_wallet" )

]
