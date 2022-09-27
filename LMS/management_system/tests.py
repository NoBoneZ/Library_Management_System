from django.test import TestCase
from django.urls import reverse

from .models import Book, BorrowedBook, BookReturn
from accounts.models import Members, Wallet


# Create your tests here.


class DebitUponBookReturnTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = Members.objects.create_user(username="TESTER", email="test@test.com", password="1234asus1234")
        test_user.save()

        test_wallet = Wallet.objects.create(owner=test_user, balance=400,)
        test_wallet.save()

        test_book = Book.objects.create(bookID=1, title='text_book')
        test_book.save()

        test_borrowed_book = BorrowedBook.objects.create(id=1, borrower=test_user, book=test_book)
        test_borrowed_book.save()

        test_book_return = BookReturn.objects.create(id=1, borrowed_book=test_borrowed_book)
        test_book_return.save()

    def test_deduction_on_acceptance_of_book_return(self):
        new_test_book = BookReturn.objects.get(id=1)
        self.client.get(reverse('management_system:approve_book_return', args=[1]))
        new_test_wallet = Wallet.objects.get(id=new_test_book.borrowed_book.borrower_id)
        self.assertEqual(new_test_wallet.balance, 395.00)

    def test_for_outstanding_debts_on_acceptance_of_book_return(self):
        new_test_book = BookReturn.objects.get(id=1)
        wallet = Wallet.objects.get(id=new_test_book.borrowed_book.borrower_id)
        wallet.balance = 0
        wallet.save()
        self.client.get(reverse('management_system:approve_book_return', args=[1]))
        check_wallet = Wallet.objects.get(id=new_test_book.borrowed_book.borrower_id)
        self.assertEqual(check_wallet.outstanding_debts, 5.00)

    def test_for_balance_when_default_plus_fee_more_than_balance(self):
        new_test_book = BorrowedBook.objects.get(id=1)
        new_test_book.debt_incurred_default = 20.0
        new_test_book.save()
        wallet = Wallet.objects.get(id=new_test_book.borrower_id)
        wallet.balance = 4.00
        wallet.outstanding_debts = 0
        wallet.save()
        self.client.get(reverse('management_system:approve_book_return', args=[1]))
        check_wallet = Wallet.objects.get(id=new_test_book.borrower_id)
        self.assertEqual(check_wallet.outstanding_debts, 21)
        self.assertEqual(check_wallet.balance, 0)

