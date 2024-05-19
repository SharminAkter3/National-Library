from django.urls import path
from .views import DepositeMoneyView, TransactionReportView, BorrowBookView
from accounts.views import PasswordChangeView


urlpatterns = [
    path("deposite/", DepositeMoneyView.as_view(), name="deposite_money"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    # path("borrow/", BorrowBookView.as_view(), name="borrow_book"),
    path("borrow/<int:id>/", BorrowBookView.as_view(), name="borrow_book"),
    # path(
    #     "password_change/",
    #     PasswordChangeView.as_view(),
    #     name="password_change",
    # ),
]
