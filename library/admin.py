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

    def save_model(self, request, obj, form, change):
        quantity = form.cleaned_data.get('quantity', 1)
        if not change:  # 仅在新添加时批量创建
            book = obj.book
            BookCopy.objects.bulk_create([
                BookCopy(book=book) for _ in range(quantity - 1)
            ])
        super().save_model(request, obj, form, change)
