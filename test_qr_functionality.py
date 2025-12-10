#!/usr/bin/env python
"""
测试二维码功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_management.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"无法设置Django环境: {e}")
    sys.exit(1)

from library.models import Book, BookCopy, User
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

print("=== 测试二维码功能 ===")

# 测试1: 检查模型是否有二维码字段
try:
    # 检查BookCopy模型是否有qr_code字段
    fields = [f.name for f in BookCopy._meta.get_fields()]
    if 'qr_code' in fields:
        print("✓ BookCopy模型已包含qr_code字段")
    else:
        print("✗ BookCopy模型缺少qr_code字段")
        print(f"现有字段: {fields}")
except Exception as e:
    print(f"✗ 检查模型字段时出错: {e}")

# 测试2: 测试二维码生成函数
try:
    # 创建一个测试图书副本
    test_book, created = Book.objects.get_or_create(
        title="测试图书",
        defaults={
            'author': '测试作者',
            'description': '测试描述',
            'copies_count': 1
        }
    )
    
    test_copy, created = BookCopy.objects.get_or_create(
        book=test_book,
        defaults={'is_available': True}
    )
    
    print(f"\n测试副本ID: {test_copy.id}")
    print(f"测试副本二维码状态: {'有二维码' if test_copy.qr_code else '无二维码'}")
    
    # 测试生成二维码
    if not test_copy.qr_code:
        print("\n测试生成二维码...")
        test_copy.generate_qr_code()
        test_copy.save()
        print(f"✓ 二维码生成成功")
        print(f"二维码文件: {test_copy.qr_code.name if test_copy.qr_code else '无'}")
    else:
        print("\n✓ 二维码已存在")
        
    # 测试二维码数据
    qr_data = f"bookcopy:{test_copy.id}"
    print(f"二维码数据: {qr_data}")
    
    # 测试get_absolute_url方法
    try:
        url = test_copy.get_absolute_url()
        print(f"二维码扫描URL: {url}")
    except Exception as e:
        print(f"✗ 获取URL时出错: {e}")
        
except Exception as e:
    print(f"✗ 测试二维码生成时出错: {e}")

# 测试3: 检查视图URL配置
try:
    from django.urls import reverse
    
    # 测试扫描URL
    scan_url = reverse('scan_qr_code', kwargs={'bookcopy_id': 1})
    print(f"\n✓ 扫描URL配置正确: {scan_url}")
    
    # 测试API URL
    api_url = reverse('qr_code_info', kwargs={'bookcopy_id': 1})
    print(f"✓ API URL配置正确: {api_url}")
    
    # 测试打印URL
    print_url = reverse('qr_code_display', kwargs={'bookcopy_id': 1})
    print(f"✓ 打印URL配置正确: {print_url}")
    
    # 测试管理URL
    management_url = reverse('qr_management', kwargs={'book_id': 1})
    print(f"✓ 管理URL配置正确: {management_url}")
    
    # 测试生成二维码URL
    generate_url = reverse('generate_qr_codes')
    print(f"✓ 生成二维码URL配置正确: {generate_url}")
    
except Exception as e:
    print(f"✗ 检查URL配置时出错: {e}")

# 测试4: 检查模板文件
template_files = [
    'library/templates/library/qr_scan.html',
    'library/templates/library/qr_mobile_scan.html',
    'library/templates/library/qr_display.html',
    'library/templates/library/qr_management.html',
]

print("\n检查模板文件:")
for template in template_files:
    if os.path.exists(template):
        print(f"✓ {template} 存在")
    else:
        print(f"✗ {template} 不存在")

print("\n=== 测试完成 ===")
print("\n使用说明:")
print("1. 运行数据库迁移: python manage.py makemigrations && python manage.py migrate")
print("2. 为现有图书生成二维码: python manage.py generate_qr_codes")
print("3. 访问二维码管理页面: /book/<book_id>/qr-management/")
print("4. 扫描二维码: /scan/<bookcopy_id>/")
print("5. 打印二维码: /qr/print/<bookcopy_id>/")

# 清理测试数据
try:
    if 'test_copy' in locals():
        test_copy.delete()
    if 'test_book' in locals():
        test_book.delete()
    print("\n✓ 测试数据已清理")
except:
    pass