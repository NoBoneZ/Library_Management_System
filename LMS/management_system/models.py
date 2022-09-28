from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import Members


# Create your models here.

class ActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class InActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class ReturnedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False, is_returned=True, is_picked=True)


class NotReturnedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_returned=False, is_picked=True)


class AnsweredManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_answered=True)


class NotAnsweredManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_answered=False)


class PickedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_picked=True)


class NotPickedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_picked=False)


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    bookID = models.AutoField(primary_key=True, unique=True, editable=False)
    title = models.CharField(max_length=500, null=True)
    genre = models.ManyToManyField(Genre)
    authors = models.TextField(
        help_text="End Every Name with a \, e.g, Adekunle, Ciroma Chukwuma/ , the main author's name should be the "
                  "first")
    thumbnail = models.ImageField(blank=True, upload_to="book_thumbnail", default="book_default.png")
    description = models.TextField(blank=True, default="No Description Available !")
    isbn = models.CharField(max_length=10, null=True, blank=True)
    isbn13 = models.CharField(max_length=13)
    average_rating = models.DecimalField(null=True, default=0.0, decimal_places=2, max_digits=3,
                                         validators=[MinValueValidator(0.0)], blank=True)
    ratings_count = models.IntegerField(null=True, default=0, validators=[MinValueValidator(0)], blank=True)
    language_code = models.CharField(max_length=7, null=True, blank=True)
    num_of_pages = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    publisher = models.CharField(max_length=500, null=True, blank=True, default="No Publisher")
    publication_date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ("-bookID",)
        unique_together = ("title", 'isbn', 'isbn13')

    def __str__(self):
        return self.title

    def quantity_lent_out(self):
        return BorrowedBook.active_objects.filter(book_id=self.bookID, is_picked=True).count()

    def quantity_available(self):
        if int(self.quantity - BorrowedBook.not_returned_objects.filter(book_id=self.bookID).count()) < 0:
            return 0
        return int(self.quantity - BorrowedBook.not_returned_objects.filter(book_id=self.bookID).count())

    def times_borrowed(self):
        return BorrowedBook.objects.filter(book_id=self.bookID).count()


class BookRequest(models.Model):
    name = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)

    objects = models.Manager()
    answered_objects = AnsweredManager()
    not_answered_objects = NotAnsweredManager()

    class Meta:
        ordering = ("-date_requested",)


class BorrowedBook(models.Model):
    borrower = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    date_borrowed = models.DateTimeField(auto_now_add=True)
    date_to_be_returned = models.DateField(null=True)
    date_returned = models.DateField(null=True, blank=True)
    debt_incurred_default = models.DecimalField(null=True, blank=True, decimal_places=2,
                                                max_digits=5, default=0.00, )
    is_picked = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    returned_objects = ReturnedManager()
    not_returned_objects = NotReturnedManager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    def __str__(self):
        return self.book.title


class RenewalRequest(models.Model):
    borrowed_book = models.ForeignKey(BorrowedBook, on_delete=models.SET_NULL, null=True)
    renewal_days = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(21)])
    new_date_of_return = models.DateField(null=True)
    date_applied = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()


class BookReturn(models.Model):
    borrowed_book = models.ForeignKey(BorrowedBook, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    def __str__(self):
        return self.borrowed_book.book.title


class BookReview(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    def __str__(self):
        return self.book.title


class ReadLater(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()
