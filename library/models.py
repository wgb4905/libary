# book_management/library/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    keywords = models.CharField(max_length=200, blank=True, null=True)
    recommended_age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    is_available = models.BooleanField(default=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_copies')
    due_date = models.DateField(null=True, blank=True)
    borrowed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - Copy {self.id}"