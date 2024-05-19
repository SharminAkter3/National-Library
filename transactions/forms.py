from django import forms
from .models import Transaction
from book.models import Book


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "transaction_type"]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account")
        super().__init__(*args, **kwargs)
        self.fields["transaction_type"].disabled = True
        self.fields["transaction_type"].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get("amount")
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"You need to deposit at least {min_deposit_amount} $"
            )

        return amount


class BorrowForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_borrwing_amount = 1
        max_borrowing_amount = 1000
        balance = account.balance
        amount = self.cleaned_data.get("amount")
        if amount < min_borrwing_amount:
            raise forms.ValidationError(f"Please select a book to borrow.")

        if amount > max_borrowing_amount:
            raise forms.ValidationError(
                f"You can withdraw at most {max_borrowing_amount} $"
            )

        if amount > balance:
            raise forms.ValidationError(f"Insufficient funds to borrow this book.")

        return amount
