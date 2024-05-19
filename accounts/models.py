from django.db import models
from django.contrib.auth.models import User
from .constants import GENDER_TYPE
from book.models import Book

# Create your models here.


class UserLibraryAccount(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.account_no)


class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name="address", on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email


class BorrowingHistory(models.Model):
    user_profile = models.OneToOneField(
        UserLibraryAccount, related_name="borrowing_history", on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, related_name="book_entity", on_delete=models.CASCADE)
    borrowing_date = models.DateTimeField(auto_now_add=True)
