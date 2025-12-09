import os
import json
import zipfile
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from library.models import Book, BookImage

class Command(BaseCommand):
    help = '批量上传图书资源（ZIP包或目录）'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str, help='ZIP文件路径或目录路径')
        parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的图书')

    def handle(self, *args, **options):
        source = options['source']
        overwrite = options['overwrite']

        if zipfile.is_zipfile(source):
            self.process_zip(source, overwrite)
        elif os.path.isdir(source):
            self.process_dir(source, overwrite)
        else:
            self.stdout.write(self.style.ERROR(f'无效的源路径: {source}'))

    def process_zip(self, zip_path, overwrite):
        with zipfile.ZipFile(zip_path) as z:
            book_dirs = [name for name in z.namelist() 
                        if name.endswith('/') and name.count('/') == 1]
            
            for book_dir in book_dirs:
                book_name = book_dir.strip('/')
                try:
                    self.process_book_in_zip(z, book_dir, book_name, overwrite)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'处理 {book_name} 失败: {str(e)}'))

    def process_dir(self, dir_path, overwrite):
        for entry in os.scandir(dir_path):
            if entry.is_dir():
                book_name = entry.name
                try:
                    self.process_book_in_dir(entry.path, book_name, overwrite)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'处理 {book_name} 失败: {str(e)}'))

    def process_book_in_zip(self, zipfile, book_dir, book_name, overwrite):
        # 处理元数据
        metadata = self._get_metadata_from_zip(zipfile, book_dir)
        if not metadata and not overwrite:
            raise Exception('无元数据且不覆盖已存在图书')

        # 创建或获取图书
        book, created = Book.objects.get_or_create(
            title=book_name,
            defaults={
                'author': metadata.get('author', '未知'),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', ''),
                'recommended_age': metadata.get('recommended_age'),
                'copies_count': metadata.get('copies_count', 1)
            }
        )

        # 处理封面
        cover_ext = self._get_image_ext_in_zip(zipfile, book_dir, prefix='封面')
        if cover_ext:
            cover_path = f"{book_dir}封面.{cover_ext}"
            book.cover_image.save(
                f"{book_name}_cover.{cover_ext}",
                File(zipfile.open(cover_path)),
                save=False
            )

        # 处理轮播图片
        gallery_dir = f"{book_dir}轮播/"
        if any(name.startswith(gallery_dir) for name in zipfile.namelist()):
            self._process_gallery_in_zip(zipfile, gallery_dir, book)

        book.save()
        self.stdout.write(self.style.SUCCESS(f'成功处理: {book_name}'))

    def process_book_in_dir(self, book_path, book_name, overwrite):
        # 处理元数据
        metadata = self._get_metadata_from_dir(book_path)
        if not metadata and not overwrite:
            raise Exception('无元数据且不覆盖已存在图书')

        # 创建或获取图书
        book, created = Book.objects.get_or_create(
            title=book_name,
            defaults={
                'author': metadata.get('author', '未知'),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', ''),
                'recommended_age': metadata.get('recommended_age'),
                'copies_count': metadata.get('copies_count', 1)
            }
        )

        # 处理封面
        cover_path = self._find_cover_in_dir(book_path)
        if cover_path:
            with open(cover_path, 'rb') as f:
                book.cover_image.save(
                    f"{book_name}_cover{os.path.splitext(cover_path)[1]}",
                    File(f),
                    save=False
                )

        # 处理轮播图片
        gallery_dir = os.path.join(book_path, '轮播')
        if os.path.exists(gallery_dir):
            self._process_gallery_in_dir(gallery_dir, book)

        book.save()
        self.stdout.write(self.style.SUCCESS(f'成功处理: {book_name}'))

    def _get_metadata_from_zip(self, zipfile, book_dir):
        for ext in ['.json', '.txt']:
            meta_path = f"{book_dir}图书信息{ext}"
            if meta_path in zipfile.namelist():
                with zipfile.open(meta_path) as f:
                    return json.load(f)
        return None

    def _get_metadata_from_dir(self, book_path):
        for ext in ['.json', '.txt']:
            meta_path = os.path.join(book_path, f'图书信息{ext}')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None

    def _get_image_ext_in_zip(self, zipfile, book_dir, prefix='封面'):
        for ext in ['jpg', 'jpeg', 'png', 'webp']:
            if f"{book_dir}{prefix}.{ext}" in zipfile.namelist():
                return ext
        return None

    def _find_cover_in_dir(self, book_path):
        for ext in ['jpg', 'jpeg', 'png', 'webp']:
            for prefix in ['封面', 'cover']:
                cover_path = os.path.join(book_path, f'{prefix}.{ext}')
                if os.path.exists(cover_path):
                    return cover_path
        return None

    def _process_gallery_in_zip(self, zipfile, gallery_dir, book):
        BookImage.objects.filter(book=book).delete()
        gallery_files = [name for name in zipfile.namelist() 
                        if name.startswith(gallery_dir) and not name.endswith('/')]
        
        for i, img_path in enumerate(gallery_files):
            BookImage.objects.create(
                book=book,
                image=File(zipfile.open(img_path)),
                caption=os.path.basename(img_path).split('.')[0],
                order=i
            )

    def _process_gallery_in_dir(self, gallery_dir, book):
        BookImage.objects.filter(book=book).delete()
        for i, filename in enumerate(sorted(os.listdir(gallery_dir))):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                img_path = os.path.join(gallery_dir, filename)
                with open(img_path, 'rb') as f:
                    BookImage.objects.create(
                        book=book,
                        image=File(f),
                        caption=os.path.splitext(filename)[0],
                        order=i
                    )
