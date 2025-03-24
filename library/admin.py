# book_management/library/admin.py
from django.contrib import admin
from .models import Book, BookCopy

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'keywords', 'recommended_age')

admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy)