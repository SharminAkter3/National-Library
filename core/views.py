from django.shortcuts import render
from category.models import Category
from book.models import Book


def home(request, category_slug=None):
    book = Book.objects.all()
    if category_slug is not None:
        category = Category.objects.get(slug=category_slug)
        book = Book.objects.filter(category=category)
    category = Category.objects.all()
    return render(request, "index.html", {"book": book, "category": category})
