from django.contrib import admin

from .models import Book, BorrowedBook, Genre, BookReturn


# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ("isbn13", "title", "quantity", "ratings_count")


admin.site.register(Book, BookAdmin)
admin.site.register(BorrowedBook)
admin.site.register(Genre)
admin.site.register(BookReturn)
