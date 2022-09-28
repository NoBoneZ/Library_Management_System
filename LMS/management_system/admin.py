from django.contrib import admin

from .models import Book, BorrowedBook, Genre, BookReturn, BookReview


# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ("isbn13", "title", "quantity", "ratings_count")


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ("member", 'book', 'date_created')


admin.site.register(Book, BookAdmin)
admin.site.register(BorrowedBook)
admin.site.register(Genre)
admin.site.register(BookReturn)
admin.site.register(BookReview,BookReviewAdmin)
