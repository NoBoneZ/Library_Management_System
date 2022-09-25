from django import forms

from .models import Book, RenewalRequest


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ("bookID", "date_added", "is_active")


class RenewalRequestForm(forms.ModelForm):
    class Meta:
        model = RenewalRequest
        fields = ("renewal_date",)


class ImportDataViaApiForm(forms.Form):
    name = forms.CharField(max_length=500, help_text="Enter the name of the Api", required=True)
    number_of_books = forms.IntegerField(help_text="Enter the amount of books you want to import, not more than 30 "
                                                   "books", required=True)
    api_link = forms.CharField(max_length=500, help_text="Enter the link for the API", required=True)
