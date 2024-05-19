from django.db import models
from category.models import Category

# Create your models here.


class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="book/media/uploads/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pdf = models.FileField(
        upload_to="book/pdfs/", blank=True, null=True
    )  # New field for PDF file

    def __str__(self):
        return self.name


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=30)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name}"
