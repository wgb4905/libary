from django.contrib import admin
from .models import Book, BookCopy
from .forms import BookCopyForm

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    form = BookCopyForm
    extra = 1  # 不显示空表单

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookCopyInline]
    list_display = ('title', 'author', 'copies_count', 'available_copies')
    
    def available_copies(self, obj):
        return obj.copies.filter(is_available=True).count()
    available_copies.short_description = '可借副本'

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    form = BookCopyForm  # 使用自定义表单

    def save_model(self, request, obj, form, change):
        quantity = form.cleaned_data.get('quantity', 1)
        if not change:  # 仅在新添加时批量创建
            book = obj.book
            BookCopy.objects.bulk_create([
                BookCopy(book=book) for _ in range(quantity - 1)
            ])
        super().save_model(request, obj, form, change)
