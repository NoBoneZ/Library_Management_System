import datetime

from management_system.models import BorrowedBook, Genre
from accounts.models import Wallet, Members


def date_checker(request):
    context = {}
    open_time = datetime.time(9, 00, 0)
    close_time = datetime.time(20, 00, 00)
    context["member"] = Members.active_objects.get(id=request.user.id) if request.user.is_authenticated else []
    context["genres"] = Genre.objects.all()
    context["open_time"] = open_time
    context["close_time"] = close_time
    if open_time <= datetime.datetime.now().time() <= close_time:
        context['is_open'] = True
        return context
    else:
        context['is_open'] = False

    return context


def default_book_checker(request):
    if datetime.datetime.now().time() == datetime.time(00,00, 00):
        not_returned_books = BorrowedBook.not_returned_objects.filter(
            date_to_be_returned__lt=datetime.datetime.now().date())
        for default_book in not_returned_books:
            number_of_days = int(str(datetime.datetime.now().date() - default_book.date_to_be_returned)[:2])
            default_book.debt_incurred_default = number_of_days * 5
            default_book.save()





