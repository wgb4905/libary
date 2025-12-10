from django.core.management.base import BaseCommand
from library.models import BookCopy
from django.utils import timezone

class Command(BaseCommand):
    help = '为所有图书副本生成二维码'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--book-id',
            type=int,
            help='仅为指定图书ID的副本生成二维码'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成所有二维码'
        )
    
    def handle(self, *args, **options):
        book_id = options.get('book_id')
        force = options.get('force')
        
        # 构建查询集
        if book_id:
            copies = BookCopy.objects.filter(book_id=book_id)
            self.stdout.write(f'为图书ID {book_id} 的副本生成二维码...')
        else:
            copies = BookCopy.objects.all()
            self.stdout.write('为所有图书副本生成二维码...')
        
        if not force:
            # 只处理没有二维码的副本
            copies = copies.filter(qr_code='') | copies.filter(qr_code__isnull=True)
        
        total = copies.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('没有需要生成二维码的图书副本'))
            return
        
        self.stdout.write(f'需要处理 {total} 个图书副本')
        
        success_count = 0
        error_count = 0
        
        for i, copy in enumerate(copies, 1):
            try:
                # 生成二维码
                copy.generate_qr_code()
                copy.save()
                success_count += 1
                
                # 显示进度
                if i % 10 == 0 or i == total:
                    self.stdout.write(f'进度: {i}/{total} ({i/total*100:.1f}%)')
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'为副本 {copy.id} 生成二维码失败: {str(e)}')
                )
        
        # 输出结果
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'二维码生成完成!'))
        self.stdout.write(f'成功: {success_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败: {error_count}'))
        
        # 统计信息
        if success_count > 0:
            self.stdout.write(f'\n统计信息:')
            self.stdout.write(f'总副本数: {BookCopy.objects.count()}')
            self.stdout.write(f'有二维码的副本: {BookCopy.objects.exclude(qr_code="").exclude(qr_code__isnull=True).count()}')
            self.stdout.write(f'无二维码的副本: {BookCopy.objects.filter(qr_code="").filter(qr_code__isnull=True).count()}')