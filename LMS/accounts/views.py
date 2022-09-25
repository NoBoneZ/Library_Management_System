from datetime import datetime

from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login, logout, authenticate
from django.views.generic import ListView

from .forms import CustomUserCreationForm, WalletPinForm
from .models import User, Inbox, Wallet
from management_system.models import BorrowedBook


# Create your views here.


def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            print(form.cleaned_data["email"])

            user_wallet = Wallet.objects.create(
                owner=User.objects.get(email=form.cleaned_data["email"])

            )

            user_wallet.save()

            print(user_wallet.wallet_number)
            print(user_wallet.pin)

            user_message = Inbox.objects.create(
                receiver=User.active_objects.get(username=request.POST.get("username")),
                sender="The Librarian",
                message=f"Welcome to Vilgax Library, A wallet has been created for you, Your wallet number is"
                        f"  {user_wallet.wallet_number} and your pin is {user_wallet.pin}....Once again, Welcome"

            )

            user_message.save()
            messages.success(request, f"welcome, {request.POST['username']}, You need to sign in")
            return HttpResponseRedirect(reverse("accounts:sign_in"))
        error = (form.errors.as_text()).split("*")
        messages.error(request, error[len(error) - 1])
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {
        "form": CustomUserCreationForm(),
        "form_type": "SIGN UP"
    }

    return render(request, "accounts/sign_in_sign_up.html", context)


def sign_in(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            messages.error(request, "User does not exist")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"welcome {user.username}")
            return HttpResponseRedirect(reverse("management_system:home"))
        messages.error(request, "Invalid Password !")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, "accounts/sign_in.html")


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("management_system:home"))


class UserInboxView(ListView):
    model = Inbox
    context_object_name = "user_messages"
    template_name = "accounts/inbox.html"

    def get_queryset(self):
        return Inbox.objects.filter(receiver_id=self.request.user.id)


class UserBorrowedBooksView(ListView):
    model = BorrowedBook
    template_name = "accounts/borrowed_books.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserBorrowedBooksView, self).get_context_data(*args, **kwargs)
        context["borrowed_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id)
        context["unpicked_books"] = BorrowedBook.objects.filter(borrower_id=self.request.user.id, is_returned=False,
                                                                is_active=True, is_picked=False)
        context["default_books"] = BorrowedBook.not_returned_objects.filter(borrower_id=self.request.user.id,
                                                                            is_picked=True,
                                                                            date_to_be_returned__lte=datetime.today().date())
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

    return render(request, "accounts/user_wallet.html", {"form": WalletPinForm()})
