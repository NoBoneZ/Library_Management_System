from django.db import models

# Create your models here.
from random import sample
from string import digits
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
#

# Create your models here.
class MembersActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class MembersInActiveManager(UserManager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class ActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class InActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class ReadManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_read=True)


class UnreadManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_read=False)


class Members(AbstractUser):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female")
    )

    username = models.CharField(max_length=15, unique=True, null=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="member_profile_picture", default='avatar.svg')
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_suspended = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
    active_objects = MembersActiveManager()
    inactive_objects = MembersInActiveManager()


class Wallet(models.Model):
    owner = models.OneToOneField(Members, on_delete=models.SET_NULL, null=True)
    wallet_number = models.UUIDField(editable=False, unique=True, null=True, default=uuid4)
    pin = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)], default=int("".join(sample(digits, 4))))
    balance = models.DecimalField(null=True, decimal_places=2, default=0.00,
                                  max_digits=35, validators=[MinValueValidator(0.0)])
    outstanding_debts = models.DecimalField(null=True, blank=True, decimal_places=2,
                                            max_digits=5, default=0.00,
                                            validators=[MaxValueValidator(500.0)])

    def __str__(self):
        return f"{self.owner.username} ---- {self.wallet_number}"

    # def save(self, *args, **kwargs):
    #     self.pin = int("".join(sample(digits, 4)))
    #     return super().save(*args, **kwargs)

    def sum_of_debit(self):
        return sum([trans.amount for trans in WalletTransaction.active_objects.filter(wallet_id=self.id)])


class WalletTransaction(models.Model):
    TRANSACTION_TYPE = (
        ("Debit", "Debit"),
        ("Credit", "Credit")
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=7, null=True)
    description = models.TextField(null=True)
    amount = models.DecimalField(null=True, decimal_places=2,
                                 max_digits=30, validators=[MinValueValidator(0.1)])
    date_occurred = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(null=True, decimal_places=2,
                                  max_digits=30, validators=[MinValueValidator(0.1)])
    outstanding_debts = models.DecimalField(null=True, blank=True, decimal_places=2,
                                            max_digits=5, default=0.00,
                                            validators=[MaxValueValidator(500.0)])

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    class Meta:
        ordering = ("-date_occurred", "wallet")


class Inbox(models.Model):
    receiver = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    sender = models.CharField(max_length=30, null=True)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    read_objects = ReadManager()
    unread_objects = UnreadManager()
    active_objects = ActiveManager()
    inactive_objects = InActiveManager()

    class Meta:
        ordering = ("-date_created",)
