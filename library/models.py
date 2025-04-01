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
    image = models.ImageField(upload_to='book_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.book.title} - 图片 {self.id}"


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    keywords = models.CharField(max_length=200, blank=True, null=True)
    recommended_age = models.IntegerField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True
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

    def __str__(self):
        return self.title
    
    def get_gallery_images(self):
        """获取所有关联图片，至少包含封面"""
        images = list(self.images.all())
        if not images and self.cover_image:
            # 如果没有上传图集，默认使用封面
            return [{'image': self.cover_image, 'caption': '封面'}]
        return images

class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    is_available = models.BooleanField(default=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_copies')
    due_date = models.DateField(null=True, blank=True)
    borrowed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - Copy {self.id}"