from django.contrib import admin
from .models import Book, BookImage, BookCopy
from .forms import BookCopyForm
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.core.files import File
from django.contrib import messages
import os
import zipfile
import json
from django.utils.html import format_html  # Added import

class BulkUploadForm(forms.Form):
    zip_file = forms.FileField(label='图书资源包(ZIP)')
    overwrite = forms.BooleanField(
        label='覆盖已存在图书',
        required=False,
        help_text='如果勾选，当图书已存在时会更新信息'
    )


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1  # 默认显示1个空表单
    fields = ('image', 'caption', 'order', 'preview')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"
    preview.short_description = '预览'

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    form = BookCopyForm
    extra = 1  # 不显示空表单
    readonly_fields = ('qr_code_preview',)  # Added field

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = '二维码预览'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookCopyInline,BookImageInline]
    list_display = ('title', 'author', 'copies_count', 'available_copies')
    
    def available_copies(self, obj):
        return obj.copies.filter(is_available=True).count()
    available_copies.short_description = '可借副本'
    

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    form = BookCopyForm  # 使用自定义表单
    list_display = ('id', 'book_title', 'is_available', 'borrower', 'due_date', 'qr_code_preview')  # Added fields
    list_filter = ('is_available', 'book')  # Added list filter
    search_fields = ('book__title', 'book__author', 'borrower__username')  # Added search fields
    readonly_fields = ('qr_code_preview',)  # Added readonly field

    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = '书名'

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = '二维码预览'

    def save_model(self, request, obj, form, change):
        quantity = form.cleaned_data.get('quantity', 1)
        if not change:  # 仅在新添加时批量创建
            book = obj.book
            BookCopy.objects.bulk_create([
                BookCopy(book=book) for _ in range(quantity - 1)
            ])
        super().save_model(request, obj, form, change)

    # 添加自定义操作
    actions = ['generate_qr_codes_action']  # Added actions

    def generate_qr_codes_action(self, request, queryset):
        """为选中的图书副本生成二维码"""
        count = 0
        for book_copy in queryset:
            if not book_copy.qr_code:
                book_copy.generate_qr_code()
                book_copy.save()
                count += 1

        self.message_user(request, f'成功为{count}个图书副本生成二维码')
    generate_qr_codes_action.short_description = '生成二维码'

