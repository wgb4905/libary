# book_management/library/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .utils import generate_book_cover
import os
from django.conf import settings

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

class BookImage(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='book_gallery/',verbose_name='详情轮播图片')
    caption = models.CharField(max_length=200, blank=True,verbose_name='图片备注')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.book.title} - 图片 {self.id}"


class Book(models.Model):
    title = models.CharField(max_length=100,verbose_name='书名')
    author = models.CharField(max_length=100,verbose_name='作者')
    description = models.TextField(verbose_name='简介')
    keywords = models.CharField(max_length=200, blank=True, null=True,verbose_name='关键字')
    recommended_age = models.IntegerField(blank=True, null=True,verbose_name='推荐年龄')
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        verbose_name='封面'
    )
    copies_count = models.PositiveIntegerField(
        default=1,
        verbose_name='副本数量',
        help_text='保存时将自动创建指定数量的副本'
    )

    def save(self, *args, **kwargs):
        if not self.pk and not self.cover_image:
            cover_path = os.path.join(settings.MEDIA_ROOT, 'book_covers', f'{self.title}_cover.png')
            generate_book_cover(
                title=self.title,
                author=self.author,
                output_path=cover_path
            )
            self.cover_image = f'book_covers/{self.title}_cover.png'
        super().save(*args, **kwargs)
    
        
        # 创建指定数量的副本
        existing_copies = self.copies.count()
        needed_copies = self.copies_count - existing_copies
        
        if needed_copies > 0:
            BookCopy.objects.bulk_create([
                BookCopy(book=self) for _ in range(needed_copies)
            ])



    def __str__(self):
        return self.title
    
    def get_gallery_images(self):
        """获取所有关联图片，至少包含封面"""
        images = list(self.images.all())
        if not images and self.cover_image:
            # 如果没有上传图集，默认使用封面
            return [{'image': self.cover_image, 'caption': '封面'}]
        return images
    
    class Meta:
        verbose_name = '书目'      # 单数形式
        verbose_name_plural = '书目'  # 复数形式（避免自动加's'）


class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    is_available = models.BooleanField(default=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_copies')
    due_date = models.DateField(null=True, blank=True)
    borrowed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.id}"
    
    class Meta:
        verbose_name = '副本'
        verbose_name_plural = '副本'