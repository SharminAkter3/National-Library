from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, BorrowForm
from .constants import DEPOSITE, BORROWING_BOOK
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from accounts.models import UserLibraryAccount, BorrowingHistory
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from book.models import Book

# from django.conf import settings
# import stripe

# stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transaction_form.html"
    model = Transaction
    title = ""
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "account": self.request.user.account,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(
            {
                "title": self.title,
            }
        )
        return context


class BorrowBookView(TransactionCreateMixin):
    form_class = DepositForm
    template_name = "transaction_form.html"
    title = "Purchase Book"

    def get_initial(self):
        initial = super().get_initial()
        book = get_object_or_404(Book, id=self.kwargs["id"])
        initial.update(
            {
                "transaction_type": BORROWING_BOOK,
                "amount": book.price,  # Set the initial amount to the book's price
            }
        )
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        user = self.request.user
        account = user.account
        book = get_object_or_404(Book, id=self.kwargs["id"])

        # Update the user's account balance
        account.balance += amount
        account.save(update_fields=["balance"])

        # Create a transaction record
        Transaction.objects.create(
            account=account,
            amount=amount,
            book=book,
            balance_after_transaction=account.balance,
            transaction_type=BORROWING_BOOK,
        )

        messages.success(
            self.request, f"You have successfully borrowed a Book for {amount}$"
        )

        mail_subject = "Book Borrowing Confirmation"
        message = render_to_string(
            "deposite_mail.html", {"user": self.request.user, "amount": amount}
        )
        to_email = self.request.user.email
        send_email = EmailMultiAlternatives(mail_subject, "", to=[to_email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

        # Set a session variable to indicate form submission
        self.request.session["price_submitted"] = True

        # Redirect to the book details page
        book_id = self.kwargs["id"]
        return redirect(reverse("details_book", kwargs={"id": book_id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs["id"])
        context["book"] = book
        context["title"] = self.title
        context["price_submitted"] = self.request.session.pop("price_submitted", False)
        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     book = get_object_or_404(Book, id=self.kwargs["id"])
    #     context["key"] = settings.STRIPE_PUBLISHABLE_KEY
    #     context["book"] = book
    #     context["title"] = self.title
    #     context["price_submitted"] = self.request.session.pop("price_submitted", False)
    #     return context

    # def charge(request):
    #     if request.method == "POST":
    #         charge = stripe.Charge.create(
    #             amount=500,
    #             currency="usd",
    #             description="Payment Gatway",
    #             source=request.POST["stripeToken"],
    #         )
    #         return render(request, "charge.html")


class DepositeMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = "Deposite"

    def get_initial(self):
        initial = {"transaction_type": DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        account.balance += amount
        account.save(update_fields=["balance"])

        messages.success(
            self.request, f"{amount}$ was deposited to your account successfully"
        )

        mail_subject = "Deposite Message"
        message = render_to_string(
            "deposite_mail.html", {"user": self.request.user, "amount": amount}
        )
        to_email = self.request.user.email
        send_email = EmailMultiAlternatives(mail_subject, "", to=[to_email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "accounts/profile.html"
    model = Transaction
    context_object_name = "report_list"

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            )
            # Calculate balance
            self.balance = queryset.aggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = self.request.user.account
        context["balance"] = self.balance
        return context
