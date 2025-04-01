from django.contrib import admin
from .models import Book, BookCopy, BookImage

class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1  # 默认显示1个空表单

@admin.register(Book)  # 使用装饰器注册，无需再次调用 admin.site.register
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'keywords', 'recommended_age')
    inlines = [BookImageInline]  # 添加内联表单

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    pass