from django.urls import path

from .views import BookDetailView, BookListView, ManagementSystemApiRoot

app_name = "management_system_api"

urlpatterns = [
    path("", ManagementSystemApiRoot.as_view(), name="api_root"),
    path("book-list/", BookListView.as_view(), name="book_list"),
    path("book-detail/<int:pk>/", BookDetailView.as_view(), name="book_detail")

]