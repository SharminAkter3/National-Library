from django.urls import path
from . import views


urlpatterns = [
    path("details/<int:id>", views.DetailBookView.as_view(), name="details_book"),
]
