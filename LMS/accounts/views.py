import datetime
import csv

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.conf.urls.static import settings
from django.contrib.auth import update_session_auth_hash, login, logout, authenticate
from django.views.generic import ListView, View
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomMembersCreationForm, WalletPinForm, RenewalRequestForm, CustomMembersChangeForm
from .models import Members, Inbox, Wallet, WalletTransaction
from management_system.models import BorrowedBook, BookReturn, RenewalRequest, BookRequest


# Create your views here.

def not_staff(request, pk):
    user = Members.active_objects.get(id=pk)
    if not user.is_staff:
        messages.error(request, "You are not allowed")
        return HttpResponseForbidden


def sign_up(request):
    if request.method == "POST":
        form = CustomMembersCreationForm(request.POST, request.FILES)

        if form.is_valid():
            member = form.save(commit=False)
            member.email = member.email.lower()
            member.username = member.username.title()
            member.save()

            print(form.cleaned_data["email"])

            member_wallet = Wallet.objects.create(
                owner=Members.active_objects.get(email=form.cleaned_data["email"])

            )

            member_wallet.save()

            member_message = Inbox.objects.create(
                receiver=Members.active_objects.get(email=form.cleaned_data["email"]),
                sender="The Librarian",
                message=f"Welcome to Vilgax Library, A wallet has been created for you, Your wallet number is"
                        f"  {member_wallet.wallet_number} and your pin is {member_wallet.pin}....Once again, Welcome"

            )

            member_message.save()
            messages.success(request, f"welcome, {request.POST['username']}, You need to sign in")
            return HttpResponseRedirect(reverse("accounts:sign_in"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {
        "form": CustomMembersCreationForm(),
        "form_type": "SIGN UP"
    }

    return render(request, "accounts/sign_in_sign_up.html", context)


def sign_in(request):
    if request.method == "POST":
        email = request.POST["email_signin"].lower()
        password = request.POST["password_signin"]

        try:
            member = Members.objects.get(email=email)
        except Members.DoesNotExist as e:
            messages.error(request, "Member does not exist")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        member = authenticate(email=email, password=password)

        if member is not None:
            login(request, member)
            messages.success(request, f"welcome {member.username}")
            return HttpResponseRedirect(reverse("management_system:home"))
        messages.error(request, "Invalid Password !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    logout(request)
    return render(request, "accounts/sign_in.html", {"form": CustomMembersCreationForm()})


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("management_system:home"))


def forgot_password(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            user = Members.active_objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)

            email_body = {
                'token': token,
                "subject": "Recover Password",
                'message': f"Hi, {user.username} , kindly reset your password by clicking "
                           f"the following link . http://{current_site}/accounts/reset_password/password-token/{uid}/{token} "
                           f"to change your password",
                "recepient": email,
            }

            send_mail(
                email_body["subject"],
                email_body["message"],
                settings.EMAIL_HOST_USER,
                [email]

            )
            print(email_body["message"])
            messages.success(request, "A password reset mail has been sent to your mail")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except Members.DoesNotExist or Exception as e:
            print(e)
            messages.error(request, "Member does not exist")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return render(request, "accounts/forgot_password.html")


def reset_password(request, uid, token):
    if request.method == "POST":
        try:
            id_decode = urlsafe_base64_decode(uid)
            user = Members.active_objects.get(id=id_decode)

            if default_token_generator.check_token(user, token):
                password = request.POST.get("password1")
                confirm_password = request.POST.get("password2")

                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    messages.success(request, "password Recovered successfully")
                    return HttpResponseRedirect(reverse("main_store:index"))
                messages.error(request, "incorrect passwords")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            else:
                messages.error(request, "Invalid Token")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except:
            messages.error(request, "Invalid link")
            return HttpResponseRedirect("accounts:sign_in")

    context = {
        "uid": urlsafe_base64_decode(uid),
        "token": Members.active_objects.get(id=urlsafe_base64_decode(uid)),

    }
    return render(request, "accounts/reset_password.html", context)


class MembersInboxView(LoginRequiredMixin, ListView):
    model = Inbox
    context_object_name = "members_messages"
    template_name = "accounts/inbox.html"
    login_url = "accounts:sign_in"

    def get_queryset(self):
        return Inbox.objects.filter(receiver_id=self.request.user.id)


class MembersBorrowedBooksView(LoginRequiredMixin, ListView):
    login_url = "accounts:sign_in"
    model = BorrowedBook
    template_name = "book_properties_page.html"

    def get_queryset(self):
        return BookRequest.not_answered_objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(MembersBorrowedBooksView, self).get_context_data(*args, **kwargs)
        bad_default_books = BorrowedBook.not_returned_objects.filter(debt_incurred_default__gte=500).values_list(
            'borrower_id')

        # context["bad_default_members"] = Members.active_objects.filter(pk__in=bad_default_books)
        context["book_requests"] = self.get_queryset()
        context["unpicked_books"] = BorrowedBook.active_objects.filter(is_picked=False, is_returned=False)
        context["book_returns"] = BookReturn.active_objects.all()
        context["all_members"] = Members.active_objects.all()
        context["suspended_members"] = Members.inactive_objects.all()
        context["renewal_requests"] = RenewalRequest.active_objects.all()
        context["borrowed_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id)
        context["user_unpicked_books"] = BorrowedBook.objects.filter(borrower_id=self.request.user.id,
                                                                     is_returned=False,
                                                                     is_active=True, is_picked=False).order_by(
            'date_borrowed')
        context["default_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id,
                                                                            is_picked=True,
                                                                            date_to_be_returned__lte=datetime.datetime.today().date())
        return context


@login_required(login_url="accounts:sign_in")
def wallet_view(request):
    try:
        wallet = Wallet.objects.get(owner_id=request.user.id)
    except Wallet.DoesNotExist:
        messages.error(request, "Wallet Does Not Exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":

        if int(request.POST.get("pin")) != wallet.pin:
            messages.error(request, "Invalid Pin")
            return HttpResponseRedirect(reverse("management_system:home"))
        messages.success(request, "It is working")
        return HttpResponseRedirect(reverse("management_system:home"))

    return render(request, "accounts/members_wallet.html", {"form": WalletPinForm()})


@login_required(login_url="accounts:sign_in")
def books_calendar_view(request):
    not_returned_books = BorrowedBook.not_returned_objects.filter(borrower_id=request.user.id)
    return render(request, "accounts/members_book_calendar.html", {"not_returned_books": not_returned_books})


@login_required(login_url="accounts:sign_in")
def make_renewal_request(request, pk):
    try:
        borrowed_book = BorrowedBook.not_returned_objects.get(id=pk, is_returned=False)
    except BorrowedBook.DoesNotExist:
        messages.error(request, "Book Does Not Exist !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        if int(request.POST.get("renewal_days")) > 21 or int(request.POST.get("renewal_days")) < 1:
            messages.error(request, "New date can not be more than 21 days or less than 1 day !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        form = RenewalRequestForm(request.POST, request.FILES)

        if form.is_valid():
            renewal = form.save(commit=False)
            renewal.borrowed_book = borrowed_book
            renewal.new_date_of_return = borrowed_book.date_to_be_returned + datetime.timedelta(
                days=form.cleaned_data.get("renewal_days"))
            renewal.save()

            print(renewal.new_date_of_return)
            messages.success(request, "renewal request sent successfully, Kindly check your inbox for updates")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, "accounts/renewal_form.html", {"form": RenewalRequestForm()})


@login_required(login_url="accounts:sign_in")
def profile_page_view(request):
    try:
        member = Members.active_objects.get(id=request.user.id)
    except Members.DoesNotExist:
        messages.success(request, "Error! Kindly contact the librarian")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        form = CustomMembersChangeForm(request.POST, request.FILES, instance=member)

        if form.is_valid():
            form.save()

            messages.success(request, "Details Updated Successfully")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        error = (form.errors.as_text()).split('*')
        messages.error(request, len(error) - 1)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    context = {
        'form': CustomMembersChangeForm(instance=member),
        "all_transactions": WalletTransaction.active_objects.filter(wallet__owner_id=request.user.id),
        "all_inbox": Inbox.objects.filter(receiver=request.user.id),
        "user_wallet": Wallet.objects.get(owner_id=request.user.id),
        "member": member,
    }

    return render(request, "accounts/profile_page.html", context)


@login_required(login_url="accounts:sign_in")
def transaction_report_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f"attachment;{request.user.username}'s_transaction_report.csv"

    writer = csv.writer(response)

    writer.writerow(["S/N", "Transaction_Type", "Amount", "Description", "Date", "Outstanding_Debts", "Balance"])

    for number, item in enumerate(
            WalletTransaction.objects.filter(wallet__owner_id=request.user.id).order_by("-date_occurred")):
        writer.writerow([(int(number) + 1), item.transaction_type, item.amount, item.description, item.date_occurred,
                         item.outstanding_debts, item.balance])

    return response


@login_required(login_url="accounts:sign_in")
def credit_wallet(request):
    try:
        wallet = Wallet.objects.get(owner_id=request.user.id)
    except Wallet.DoesNotExist:
        messages.error(request, "Error , Wallet Not found")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":

        if wallet.pin != int(request.POST.get("pin")):
            messages.error(request, "Wrong pin, You will be logged out now")
            logout(request)
            return HttpResponseRedirect(reverse("accounts:sign_in"))
        wallet.balance += int(request.POST.get("amount"))
        wallet.save()

        if wallet.outstanding_debts > 0:
            wallet.balance = wallet.balance - wallet.outstanding_debts
            if wallet.balance < 0:
                wallet.outstanding_debts = abs(wallet.balance)
            else:
                wallet.outstanding_debts = 0
        wallet.save()

        wallet_transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="Credit",
            amount=int(request.POST.get('amount')),
            description=f"Credited account with {int(request.POST.get('amount'))}"

        )
        wallet_transaction.save()
        messages.success(request, f"{wallet.wallet_number} credited with {request.POST.get('amount')} successfullly")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
