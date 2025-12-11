# book_management/library/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from .utils import generate_book_cover
import os
from django.conf import settings
from django.urls import reverse

# 尝试导入qrcode，如果失败则提供替代方案
try:
    import qrcode
    from io import BytesIO
    from django.core.files.base import ContentFile
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("警告: qrcode库未安装，二维码功能将受限")
    print("请运行: pip install qrcode[pil]")

class User(AbstractUser):
    is_admin = models.BooleanField(default=False, verbose_name='管理员')
    
    # 明确指定groups和user_permissions的through模型
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="library_user_set",
        related_query_name="library_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="library_user_set",
        related_query_name="library_user",
    )
    
    class Meta:
        db_table = 'library_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

# 先定义Book模型，这样BookImage可以引用它
class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    description = models.TextField(verbose_name='简介')
    keywords = models.CharField(max_length=200, blank=True, null=True, verbose_name='关键字')
    recommended_age = models.IntegerField(blank=True, null=True, verbose_name='推荐年龄')
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
        db_table = 'library_book'
        verbose_name = '书目'
        verbose_name_plural = '书目'

class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images', verbose_name='所属图书')
    image = models.ImageField(upload_to='book_gallery/', verbose_name='详情轮播图片')
    caption = models.CharField(max_length=200, blank=True, verbose_name='图片备注')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'library_bookimage'
        ordering = ['order']
        verbose_name = '图书图片'
        verbose_name_plural = '图书图片'

    def __str__(self):
        return f"{self.book.title} - 图片 {self.id}"

class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies', verbose_name='所属图书')
    is_available = models.BooleanField(default=True, verbose_name='可借状态')
    borrower = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='borrowed_copies', verbose_name='借阅者')
    due_date = models.DateField(null=True, blank=True, verbose_name='应还日期')
    borrowed_date = models.DateField(null=True, blank=True, verbose_name='借阅日期')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='二维码')

    def __str__(self):
        return f"{self.book.title} - 副本 {self.id}"
    
    def save(self, *args, **kwargs):
        # 如果是新创建的副本，生成二维码
        if not self.pk or not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        """生成图书副本的二维码"""
        if not QRCODE_AVAILABLE:
            # 如果没有安装qrcode，跳过生成
            return
            
        try:
            # 创建二维码数据
            qr_data = f"bookcopy:{self.id}"
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # 创建二维码图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 将图片保存到内存
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            # 保存到模型字段
            filename = f'qr_code_bookcopy_{self.id}.png'
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        except Exception as e:
            print(f"生成二维码失败: {e}")
    
    def get_absolute_url(self):
        """获取二维码扫描URL"""
        return reverse('scan_qr_code', kwargs={'bookcopy_id': self.id})
    
    class Meta:
        db_table = 'library_bookcopy'
        verbose_name = '副本'
        verbose_name_plural = '副本'