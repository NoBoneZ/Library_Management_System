import datetime
import io
import csv

from django.shortcuts import render, reverse
from django.db.models import Q, Count
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.views.generic import DetailView, View, ListView
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from .models import Genre, Book, BorrowedBook, BookRequest, BookReturn, RenewalRequest
from .forms import BookForm, ImportDataViaApiForm
from accounts.models import Members, Inbox, Wallet, WalletTransaction


# Create your views here.
def popular_books():
    times_borrowed_list = [ind_book.times_borrowed() for ind_book in Book.active_objects.all()]
    times_borrowed_list.sort(reverse=True)
    return [pop_book for pop_book in Book.active_objects.all()
            if pop_book.times_borrowed() in times_borrowed_list[:10]][:10]


def high_paying_customers():
    sum_of_debit = [high_pay.sum_of_debit() for high_pay in Wallet.objects.all()]
    sum_of_debit.sort(reverse=True)
    return [customers for customers in Wallet.objects.all()
            if customers.sum_of_debit() in sum_of_debit[:10]][:10]


def report_to_pdf(header: str, object_list):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 12)

    pdf_list = []
    pdf_list.insert(0, header)

    for obj in object_list:
        pdf_list.append(obj)

    for number, lines in enumerate(pdf_list):
        if number == 0:
            textob.textLines(lines)
            textob.textLines("+++++++++++++++")
            textob.textLines("  ")
            continue
        textob.textLines(str(lines))
        textob.textLines("  ")

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return buf


def report_to_csv(file_name: str, header_list: [], queryset, object_values_list: []):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f'attachment;filename={file_name}.csv'

    writer = csv.writer(response)

    writer.writerow([header_list])

    for item in queryset:
        writer.writerow([object_values_list])

    return response


def home(request):
    search = request.GET.get("search") if request.GET.get("search") is not None else " "

    list_of_books = Book.active_objects.filter(Q(title__icontains=search) | Q(authors__icontains=search)
                                               | Q(genre__name__iexact=search)
                                               )

    book_checker = list(BookRequest.not_answered_objects.filter(name_id=request.user.id))
    book_checker += list(BorrowedBook.not_returned_objects.filter(borrower_id=request.user.id))

    open_time = datetime.time(9, 00, 0)
    close_time = datetime.time(20, 00, 00)
    if open_time <= datetime.datetime.now().time() <= close_time:
        is_open = True
    else:
        is_open = False

    context = {
        # "genres": Genre.objects.all(),
        "books": list_of_books,
        "members_book_request": [book_request.book_id
                                 for book_request in book_checker] if request.user.is_authenticated else [],
        "popular_books": popular_books()[:5],
        "open_time": open_time,
        'close_time': close_time,
        "is_open": is_open,

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

        book_request = BookRequest.objects.get_or_create(name=Members.active_objects.get(id=self.request.user.id),
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
        bad_default_books = BorrowedBook.not_returned_objects.filter(debt_incurred_default__gte=500).values_list(
            'borrower_id')

        context["bad_default_members"] = Members.active_objects.filter(pk__in=bad_default_books)
        context["book_requests"] = self.get_queryset()
        context["unpicked_books"] = BorrowedBook.active_objects.filter(is_picked=False, is_returned=False)
        context["book_returns"] = BookReturn.active_objects.all()
        context["all_members"] = Members.active_objects.all()
        context["suspended_members"] = Members.inactive_objects.all()
        context["renewal_requests"] = RenewalRequest.active_objects.all()
        return context


class AcceptBookRequestView(View):
    def get(self, request, *args, **kwargs):
        try:
            book_request = BookRequest.not_answered_objects.get(id=kwargs["pk"])
        except BookRequest.DoesNotExist:
            messages.error(request, "Book Request Does Not Exist !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        borrowed_book = BorrowedBook.objects.create(
            borrower=Members.objects.get(id=book_request.name_id),
            book=Book.active_objects.get(bookID=book_request.book_id),
            date_to_be_returned=datetime.datetime.now().date() + datetime.timedelta(days=21)

        )
        borrowed_book.save()

        message = Inbox.objects.create(
            receiver=Members.objects.get(id=book_request.name_id),
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
            receiver=Members.objects.get(id=book_request.name_id),
            sender="The Library",
            message=f"We are Sorry, {book_request.book} is currently Unavailable for you, Please Try again later, "
                    f"Thank You ! :) "
        )
        message.save()

        book_request.is_answered = True
        book_request.save()
        messages.success(request, "Book request Rejected Successfully !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


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
        messages.error(request, "Error, Kindly contact the Administrator !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    book_return.is_active = False
    book_return.is_approved = True
    book_return.save()

    try:
        borrowed_book = BorrowedBook.active_objects.get(id=book_return.borrowed_book_id)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "Error, Kindly contact the Administrator !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    borrowed_book.is_active = False
    borrowed_book.is_returned = True
    borrowed_book.save()

    try:
        member_wallet = Wallet.objects.get(owner_id=book_return.borrowed_book.borrower_id)
    except:
        messages.error(request, "Wallet Not Found, Contact Admin")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    # if member_wallet.balance < 5:
    #     member_wallet.outstanding_debts += (5 + borrowed_book.debt_incurred_default) - member_wallet.balance
    #     member_wallet.balance = 0
    #     member_wallet.save()
    #
    # else:
    if (member_wallet.balance - (5 + borrowed_book.debt_incurred_default)) < 0:
        member_wallet.balance -= (5 + borrowed_book.debt_incurred_default)
        member_wallet.outstanding_debts += abs(member_wallet.balance)
        member_wallet.balance = 0
        member_wallet.save()
    else:
        member_wallet.balance -= (5 + borrowed_book.debt_incurred_default)
        member_wallet.save()

    member_wallet_transaction = WalletTransaction.objects.create(
        wallet=member_wallet,
        transaction_type="Debit",
        description=f"Fee on the return of {borrowed_book.book}",
        amount=5,
        balance=member_wallet.balance,
        outstanding_debts=member_wallet.outstanding_debts,

    )
    member_wallet_transaction.save()

    member_message = Inbox.objects.create(
        receiver=Members.active_objects.get(id=book_return.borrowed_book.borrower_id),
        sender="The library",
        message=f"Your book return has been approved, You have been charged the standard Rs.5 .Thank you"

    )
    member_message.save()

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

    member_message = Inbox.objects.create(
        receiver=Members.objects.get(id=book_return.borrowed_book.borrower_id),
        sender="The Library",
        message=f"Your Book Return Has Been Disapproved, kindly contact the librarian ASAP, as you will still be charged"
                f"per day, until it is cleared"
    )
    member_message.save()
    messages.success(request, "Book Return Disapproved successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ReportView(ListView):
    model = Book
    template_name = "management_system/report.html"

    def get_queryset(self):
        return Book.active_objects.all()

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        context["all_books"] = self.get_queryset()
        context["popular_books"] = popular_books()
        context["high_paying_customers"] = high_paying_customers()
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


def high_paying_customer_pdf(request):
    header = "List of High Paying Customers."
    the_pdf = report_to_pdf(header, high_paying_customers())
    return FileResponse(the_pdf, as_attachment=True, filename="High_paying_customers.pdf")


def popular_books_pdf(request):
    header = "List Of Popular Books."
    the_pdf = report_to_pdf(header, popular_books())
    return FileResponse(the_pdf, as_attachment=True, filename="Popular_Books.pdf")


def suspend_unsuspend_member(request, username):
    try:
        chosen_member = Members.objects.get(username=username)
    except Members.DoesNotExist:
        messages.error(request, "Error! , contact the Admin")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    chosen_member.is_active = not chosen_member.is_active
    chosen_member.save()
    messages.success(request, "Member action Taken Successfully")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def test_(request):
    return render(request, "403.html")


class AcceptRenewalRequestView(View):
    def get(self, request, *args, **kwargs):
        try:
            renewal_request = RenewalRequest.active_objects.get(id=kwargs["pk"])
        except RenewalRequest.DoesNotExist:
            messages.error(request, "Error! kindly contact the Admin")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        try:
            borrowed_book = BorrowedBook.not_returned_objects.get(id=renewal_request.borrowed_book_id)
        except BorrowedBook.DoesNotExist:
            messages.error(request, "Error! kindly contact the Admin")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        borrowed_book.date_to_be_returned = borrowed_book.date_to_be_returned + datetime.timedelta(
            days=renewal_request.renewal_days)
        renewal_request.is_approved = True
        renewal_request.is_active = True

        member_message = Inbox.objects.create(
            receiver=Members.active_objects.get(id=borrowed_book.borrower_id),
            sender="The library",
            message=f"Your renewal request for {borrowed_book.book} has been approved !"

        )

        member_message.save()
        borrowed_book.save()
        renewal_request.save()

        messages.success(request, "Renewal Accepted Successfully !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class RejectRenewalRequestView(View):
    def get(self, request, *args, **kwargs):
        try:
            renewal_request = RenewalRequest.active_objects.get(id=kwargs["pk"])
        except RenewalRequest.DoesNotExist:
            messages.error(request, "Error! kindly contact the Admin")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        renewal_request.is_active = False
        renewal_request.save()

        member_message = Inbox.objects.create(
            receiver=Members.active_objects.get(id=renewal_request.borrowed_book.borrower_id),
            sender="The library",
            message=f"Your renewal request for {renewal_request.borrowed_book.book} has been Rejected!, "
                    f"make the return on time to avoid being charged the default fee"

        )

        member_message.save()

        messages.success(request, "Renewal Rejected Successfully !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def book_stock_report_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f'attachment;filename=Book_stock_report.csv'

    writer = csv.writer(response)

    writer.writerow(["S/N", "Title", "Quantity in the Library", "Quantity lent out", "Total stock"])

    for item in Book.active_objects.all().order_by("bookID"):
        print(item)
        writer.writerow([item.bookID, item.title, item.quantity_available(), item.quantity_lent_out(), item.quantity])

    return response


def popular_books_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f"attachment;popular_books.csv"

    writer = csv.writer(response)

    writer.writerow(["S/N", "Title", "Times_lent", "Quantity in the library", "Total_Stock"])

    for number, item in enumerate(popular_books()):
        writer.writerow([(int(number) + 1), item.title, item.times_borrowed(), item.quantity_available(), item.quantity])

    return response


def high_paying_customers_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f"High_Paying_Customers.csv"

    writer = csv.writer(response)

    writer.writerow(["S/N", "Owner", "Wallet_ID", "Amount Spent", "Current Balance"])

    for number, item in enumerate(high_paying_customers()):
        writer.writerow(
            [(int(number) + 1), item.owner.username, item.wallet_number, item.sum_of_debit(), item.balance])

    return response

