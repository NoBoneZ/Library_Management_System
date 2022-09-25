import datetime

from django.shortcuts import render, reverse
from django.db.models import Q, Count
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View, ListView
import requests

from .models import Genre, Book, BorrowedBook, BookRequest, BookReturn
from .forms import BookForm, RenewalRequestForm, ImportDataViaApiForm
from accounts.models import User, Inbox, Wallet


# Create your views here.


def home(request):
    search = request.GET.get("search") if request.GET.get("search") is not None else " "

    list_of_books = Book.active_objects.filter(Q(title__icontains=search) | Q(authors__icontains=search)
                                               | Q(genre__name__iexact=search)
                                               )

    book_checker = list(BookRequest.not_answered_objects.filter(name_id=request.user.id))
    book_checker += list(BorrowedBook.not_returned_objects.filter(borrower_id=request.user.id))

    context = {
        "genres": Genre.objects.all(),
        "books": list_of_books,
        "user_book_request": [book_request.book_id
                              for book_request in book_checker] if request.user.is_authenticated else [],

    }
    return render(request, "management_system/home.html", context)


def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, f"{request.POST['title']} added successfully !")
            return HttpResponseRedirect(reverse("management_system:home"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
    return render(request, "management_system/add_book.html", {"form": BookForm()})


def edit_book_details(request, pk):
    try:
        book = Book.active_objects.get(bookID=pk)
    except Book.DoesNotExist:
        messages.error(request, "The book does not exist !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()

            messages.success(request, f"{request.POST['title']} updated Successfully !")
            return HttpResponseRedirect(reverse("management_system:home"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, 'management_system/add_book.html', {"form": BookForm(instance=book)})


def delete_book(request, pk):
    try:
        book = Book.active_objects.get(bookID=pk)
    except Book.DoesNotExist:
        messages.error(request, "The book does not exist !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    book.is_active = False
    book.save()
    return HttpResponseRedirect(reverse("management_system:home"))


class BookDetailView(DetailView):
    model = Book
    context_object_name = "single_book"


class MakeBookRequestView(View):
    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(owner_id=request.user.id)

        if wallet.outstanding_debts >= 490:
            messages.error(request, "Your Outstanding debts is too much, Kindly settle some !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        book_request = BookRequest.objects.get_or_create(name=User.active_objects.get(id=request.user.id),
                                                         book=Book.active_objects.get(pk=self.kwargs["pk"]))[0]

        book_request.is_answered = False
        book_request.date_requested = datetime.datetime.now()
        book_request.save()
        messages.success(request, "Your book request has been sent to the librarian , kindly check your inbox for "
                                  "Updates")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def pick_unpicked_books(request, pk):
    try:
        borrowed_book = BorrowedBook.active_objects.get(id=pk)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "This book does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    borrowed_book.is_picked = True
    borrowed_book.save()

    messages.success(request, "Book picked successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def delete_unpicked_books(request, pk):
    try:
        borrowed_book = BorrowedBook.active_objects.get(id=pk)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "Book does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    borrowed_book.is_active = False
    borrowed_book.save()

    messages.success(request, "Book deleted successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class LibrarianBookRequestView(ListView):
    model = BookRequest
    template_name = "management_system/librarian_book_request_page.html"

    def get_queryset(self):
        return BookRequest.not_answered_objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(LibrarianBookRequestView, self).get_context_data(*args, **kwargs)
        print(BookReturn.objects.all())
        context["book_requests"] = self.get_queryset()
        context["unpicked_books"] = BorrowedBook.active_objects.filter(is_picked=False, is_returned=False)
        context["book_returns"] = BookReturn.active_objects.all()
        return context


class AcceptBookRequestView(View):
    def get(self, request, *args, **kwargs):
        try:
            book_request = BookRequest.not_answered_objects.get(id=kwargs["pk"])
        except BookRequest.DoesNotExist:
            messages.error(request, "Book Request Does Not Exist !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        borrowed_book = BorrowedBook.objects.create(
            borrower=User.objects.get(id=book_request.name_id),
            book=Book.active_objects.get(bookID=book_request.book_id),
            date_to_be_returned=datetime.datetime.now().date() + datetime.timedelta(days=21)

        )
        borrowed_book.save()

        message = Inbox.objects.create(
            receiver=User.objects.get(id=book_request.name_id),
            sender="The Library",
            message=f"Your request to lend {borrowed_book.book.title} has been approved, you are to pick it up "
                    f"immediately, and return it on or "
                    f"before {borrowed_book.date_to_be_returned}.If you want to apply for a renewal, that should be made"
                    f"at least 5 days before{borrowed_book.date_to_be_returned}. Upon returning the book you will be "
                    f"charged Rs.5. IT IS IMPORTANT TO NOTE THAT, IF YOU DEFAULT THE RETURN DATE, "
                    f"YOU WILL BE CHARGED Rs.5, per day. Thank you! :)"
        )
        message.save()

        book_request.is_answered = True
        book_request.save()

        messages.success(request, "Book request accepted Successfully !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class RejectBookRequestView(View):
    def get(self, request, *args, **kwargs):
        try:
            book_request = BookRequest.not_answered_objects.get(id=kwargs["pk"])
        except BookRequest.DoesNotExist:
            messages.error(request, "Book Request Does Not Exist !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        message = Inbox.objects.create(
            receiver=User.objects.get(id=book_request.name_id),
            sender="The Library",
            message=f"We are Sorry, {book_request.book} is currently Unavailable for you, Please Try again later, "
                    f"Thank You ! :) "
        )
        message.save()

        book_request.is_answered = True
        book_request.save()
        messages.success(request, "Book request Rejected Successfully !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def make_renewal_request(request, pk):
    try:
        borrowed_book = BorrowedBook.active_objects.get(id=pk, is_returned=False)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "Book Does Not Exist !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        if request.POST.get("renewal_date") >= datetime.datetime.today().date() + datetime.timedelta(days=14):
            messages.error(request, "New date can not be more than 40 days from today !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        form = RenewalRequestForm(request.POST, request.FILES)

        if form.is_valid():
            renewal = form.save(commit=False)
            renewal.borrowed_book = borrowed_book
            renewal.save()

            messages.success(request, "renewal request sent successfully, Kindly check your inbox for updates")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, "management_system/add_book.html", {"form": RenewalRequestForm()})


class MakeBookReturnsView(View):
    def get(self, request, *args, **kwargs):
        try:
            borrowed_book = BorrowedBook.active_objects.get(id=kwargs["pk"])
        except BorrowedBook.DoesNotExist:
            messages.error(request, "Error! Kindly Contact The Librarian")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        book_return = BookReturn.objects.get_or_create(
            borrowed_book=borrowed_book,

        )[0]
        book_return.save()

        messages.success(request, "The librarian would check and approve it in a bit")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def approve_book_return(request, pk):
    try:
        book_return = BookReturn.active_objects.get(id=pk)
    except BookReturn.DoesNotExist:
        messages.error(request, "Error, Kindly contact the Librarian !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    book_return.is_active = False
    book_return.is_approved = True
    book_return.save()

    try:
        borrowed_book = BorrowedBook.active_objects.get(id=book_return.borrowed_book_id)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "Error, Kindly contact the Librarian !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    borrowed_book.is_active = False
    borrowed_book.is_returned = True
    borrowed_book.save()

    user_message = Inbox.objects.create(
        receiver=User.active_objects.get(id=book_return.borrowed_book.borrower_id),
        sender="The library",
        message=f"Your book return has been approved, thank you"

    )
    user_message.save()

    messages.success(request, "Book Return Approve successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def reject_book_return(request, pk):
    try:
        book_return = BookReturn.active_objects.get(id=pk)
    except BookReturn.DoesNotExist:
        messages.error(request, "Error, Kindly contact the Librarian !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    book_return.is_active = False
    book_return.is_approved = False
    book_return.save()

    user_message = Inbox.objects.create(
        receiver=User.objects.get(id=book_return.borrowed_book.borrower_id),
        sender="The Library",
        message=f"Your Book Return Has Been Disapproved, kindly contact the librarian ASAP, as you will still be charged"
                f"per day, until it is cleared"
    )
    user_message.save()
    messages.success(request, "Book Return Disapproved successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ReportView(ListView):
    model = Book
    template_name = "management_system/report.html"

    def get_queryset(self):
        return Book.active_objects.all()

    def get_context_data(self, **kwargs):
        times_borrowed_list = [ind_book.times_borrowed() for ind_book in self.get_queryset()]
        sum_of_debit = [high_pay.sum_of_debit() for high_pay in Wallet.objects.all()]

        times_borrowed_list.sort()
        sum_of_debit.sort()

        context = super(ReportView, self).get_context_data(**kwargs)
        context["all_books"] = self.get_queryset()
        context["popular_books"] = [pop_book for pop_book in self.get_queryset()
                                    if pop_book.times_borrowed() in times_borrowed_list[:10]]
        context["high_paying_customers"] = [customers for customers in Wallet.objects.all()
                                            if customers.sum_of_debit() in sum_of_debit[:10]]
        return context


class ImportDataViaApiView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "management_system/data_import.html", {"form": ImportDataViaApiForm()})

    def post(self, request, *args, **kwargs):
        number_of_books = int(request.POST.get("number_of_books"))
        if number_of_books > 30 or number_of_books < 1:
            messages.error(request, "invalid amount of books")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if request.POST["name"] is not None:
            name = request.POST.get("name")
            url = request.POST.get("api_link")
            response = requests.get(url)
            data = response.json()

            try:
                books = data[name]
            except:
                messages.error(request, "Error! Invalid Name")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            for book in books[:number_of_books]:
                try:
                    new_book = Book.objects.create(
                        title=book.get("title"),
                        authors=book.get("authors"),
                        average_rating=book.get("average_rating"),
                        isbn=book.get("isbn"),
                        isbn13=book.get("isbn13"),
                        language_code=book.get("language_code"),
                        num_of_pages=book.get("num_pages"),
                        ratings_count=book.get("ratings_count"),
                        publisher=book.get("publisher")
                    )
                    new_book.save()
                except:
                    continue
            messages.success(request, f"{number_of_books} Books added successfully")
            return HttpResponseRedirect(reverse("management_system:home"))
