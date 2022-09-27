import datetime
import csv

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.conf.urls.static import settings
from django.contrib.auth import update_session_auth_hash, login, logout, authenticate
from django.views.generic import ListView, View
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from .forms import CustomMembersCreationForm, WalletPinForm, RenewalRequestForm, CustomMembersChangeForm
from .models import Members, Inbox, Wallet, WalletTransaction
from management_system.models import BorrowedBook


# Create your views here.


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
                owner=Members.objects.get(email=form.cleaned_data["email"])

            )

            member_wallet.save()

            member_message = Inbox.objects.create(
                receiver=Members.active_objects.get(username=request.POST.get("username")),
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
    return render(request, "accounts/sign_in.html", {"form": CustomMembersCreationForm()})


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("management_system:home"))


def forgot_password(request):
    if request.method == "POST":
        print(request.POST.get("email"))
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


class MembersInboxView(ListView):
    model = Inbox
    context_object_name = "members_messages"
    template_name = "accounts/inbox.html"

    def get_queryset(self):
        return Inbox.objects.filter(receiver_id=self.request.user.id)


class MembersBorrowedBooksView(ListView):
    model = BorrowedBook
    template_name = "accounts/borrowed_books.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MembersBorrowedBooksView, self).get_context_data(*args, **kwargs)
        context["borrowed_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id)
        context["unpicked_books"] = BorrowedBook.objects.filter(borrower_id=self.request.user.id, is_returned=False,
                                                                is_active=True, is_picked=False)
        context["default_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id,
                                                                            is_picked=True,
                                                                            date_to_be_returned__lte=datetime.datetime.today().date())
        return context


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


def books_calendar_view(request):
    not_returned_books = BorrowedBook.not_returned_objects.filter(borrower_id=request.user.id)
    return render(request, "accounts/members_book_calendar.html", {"not_returned_books": not_returned_books})


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

            messages.success(request, "renewal request sent successfully, Kindly check your inbox for updates")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, "management_system/add_book.html", {"form": RenewalRequestForm()})


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
        "member":member,
    }

    return render(request, "accounts/profile_page.html", context)


def transaction_report_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content_Disposition"] = f"attachment;{request.user.username}'s_transaction_report.csv"

    writer = csv.writer(response)

    writer.writerow(["S/N", "Transaction_Type", "Amount", "Description", "Date", "Outstanding_Debts", "Balance"])

    for number, item in enumerate(WalletTransaction.objects.filter(wallet__owner_id=request.user.id).order_by("-date_occurred")):
        writer.writerow([(int(number) + 1), item.transaction_type, item.amount, item.description, item.date_occurred, item.outstanding_debts, item.balance ])

    return response
