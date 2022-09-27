from django.urls import path

from .views import (home,
                    add_book,
                    edit_book_details,
                    delete_book,
                    MakeBookRequestView,
                    LibrarianBookRequestView,
                    AcceptBookRequestView,
                    RejectBookRequestView,
                    pick_unpicked_books,
                    delete_unpicked_books,
                    MakeBookReturnsView,
                    approve_book_return,
                    reject_book_return,
                    ReportView,
                    ImportDataViaApiView,
                    suspend_unsuspend_member,
                    test_,
                    high_paying_customer_pdf,
                    popular_books_pdf,
                    RejectRenewalRequestView,
                    AcceptRenewalRequestView,
                    book_stock_report_csv,
                    popular_books_csv,
                    high_paying_customers_csv
                    )

app_name = 'management_system'

urlpatterns = [
    path("", home, name="home"),
    path("add_book/", add_book, name="add_book"),
    path("edit_book_details/<int:pk>", edit_book_details, name="edit_book_details"),
    path("delete_book/<int:pk>", delete_book, name="delete_book"),

    path("make_book_request/<int:pk>", MakeBookRequestView.as_view(), name='book_request'),

    path("librarian_book_request/", LibrarianBookRequestView.as_view(), name="librarian_book_page"),
    path("accept_book_request/<int:pk>", AcceptBookRequestView.as_view(), name='accept_book_request'),
    path("reject_book_request/<int:pk>", RejectBookRequestView.as_view(), name='reject_book_request'),

    path("pick_unpicked_book/<int:pk>", pick_unpicked_books, name="pick_unpicked_books"),
    path("delete_unpicked_book/<int:pk>", delete_unpicked_books, name="delete_unpicked_books"),

    path("make_book_return/<int:pk>", MakeBookReturnsView.as_view(), name="make_book_return"),
    path("approve_book_return/<int:pk>", approve_book_return, name="approve_book_return"),
    path("reject_book_return/<int:pk>", reject_book_return, name="reject_book_return"),

    path("library_report/", ReportView.as_view(), name="library_report"),
    path("book_stock_report_csv/", book_stock_report_csv, name="book_stock_csv"),
    path("popular_books_csv/", popular_books_csv, name="popular_books_csv"),
    path("high_paying_customers_csv/", high_paying_customers_csv, name="high_paying_customers_csv"),


    path("import_books_via_api/", ImportDataViaApiView.as_view(), name="import_data"),
    path("suspend_member/<str:username>/", suspend_unsuspend_member, name="suspend_unsuspend_member"),

    path("reject_renewal_request/<int:pk>", RejectRenewalRequestView.as_view(), name="reject_renewal"),
    path("accept_renewal_request/<int:pk>", AcceptRenewalRequestView.as_view(), name="accept_renewal"),

    path("403/", test_, name='test'),

    path("high_paying_customers_pdf/", high_paying_customer_pdf, name="high_paying_customers_pdf"),
    path("popular_books_pdf/", popular_books_pdf, name="popular_books_pdf")

]
