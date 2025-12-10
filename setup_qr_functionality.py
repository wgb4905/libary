#!/usr/bin/env python
"""
二维码功能部署脚本
"""

import os
import sys
import subprocess
import time

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(cmd, description):
    print(f"\n{description}...")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description}成功")
            if result.stdout:
                print(f"输出: {result.stdout[:200]}...")
            return True
        else:
            print(f"✗ {description}失败")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 执行命令时出错: {e}")
        return False

def check_file_exists(filepath):
    if os.path.exists(filepath):
        print(f"✓ {filepath} 存在")
        return True
    else:
        print(f"✗ {filepath} 不存在")
        return False

def main():
    print_header("图书管理程序二维码功能部署脚本")
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查是否在正确目录
    manage_py = os.path.join(current_dir, "manage.py")
    if not os.path.exists(manage_py):
        print("\n⚠ 警告: 未找到manage.py文件")
        print("请确保在Django项目根目录运行此脚本")
        return
    
    # 步骤1: 检查依赖
    print_header("步骤1: 检查依赖")
    
    dependencies = [
        ("qrcode", "二维码生成库"),
        ("Pillow", "图像处理库"),
        ("django", "Django框架"),
    ]
    
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} ({desc}) 已安装")
        except ImportError:
            print(f"✗ {dep} ({desc}) 未安装")
            install = input(f"是否安装 {dep}? (y/n): ")
            if install.lower() == 'y':
                run_command(f"pip install {dep}", f"安装 {dep}")
    
    # 步骤2: 检查文件完整性
    print_header("步骤2: 检查文件完整性")
    
    required_files = [
        "library/models.py",
        "library/views.py",
        "library/urls.py",
        "library/admin.py",
        "library/management/commands/generate_qr_codes.py",
        "library/templates/library/qr_scan.html",
        "library/templates/library/qr_mobile_scan.html",
        "library/templates/library/qr_display.html",
        "library/templates/library/qr_management.html",
    ]
    
    all_files_exist = True
    for file in required_files:
        if not check_file_exists(file):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n⚠ 警告: 部分文件缺失，二维码功能可能不完整")
        continue_deploy = input("是否继续部署? (y/n): ")
        if continue_deploy.lower() != 'y':
            return
    
    # 步骤3: 数据库迁移
    print_header("步骤3: 数据库迁移")
    
    print("\n检查模型变更...")
    # 检查BookCopy模型是否有qr_code字段
    models_content = ""
    try:
        with open("library/models.py", "r", encoding="utf-8") as f:
            models_content = f.read()
    except:
        pass
    
    if "qr_code = models.ImageField" in models_content:
        print("✓ 模型已包含二维码字段")
        
        # 创建迁移文件
        run_command(
            "python manage.py makemigrations library",
            "创建数据库迁移文件"
        )
        
        # 应用迁移
        run_command(
            "python manage.py migrate",
            "应用数据库迁移"
        )
    else:
        print("✗ 模型未包含二维码字段")
        print("请确保已正确修改models.py文件")
    
    # 步骤4: 创建必要目录
    print_header("步骤4: 创建必要目录")
    
    directories = [
        "media/qr_codes",
        "media/book_covers",
        "media/book_gallery",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    # 步骤5: 测试功能
    print_header("步骤5: 测试功能")
    
    print("\n运行功能测试...")
    test_file = "test_qr_functionality.py"
    if os.path.exists(test_file):
        run_command(f"python {test_file}", "运行功能测试")
    else:
        print(f"✗ 测试文件 {test_file} 不存在")
    
    # 步骤6: 生成初始二维码
    print_header("步骤6: 生成初始二维码")
    
    generate_qr = input("\n是否为现有图书生成二维码? (y/n): ")
    if generate_qr.lower() == 'y':
        run_command(
            "python manage.py generate_qr_codes",
            "为所有图书副本生成二维码"
        )
    
    # 步骤7: 启动开发服务器测试
    print_header("步骤7: 启动测试")
    
    print("\n启动开发服务器进行测试...")
    print("按 Ctrl+C 停止服务器")
    print("\n测试URL:")
    print("1. 图书列表: http://127.0.0.1:8000/")
    print("2. 二维码管理示例: http://127.0.0.1:8000/book/1/qr-management/")
    print("3. 二维码扫描示例: http://127.0.0.1:8000/scan/1/")
    print("4. 二维码打印示例: http://127.0.0.1:8000/qr/print/1/")
    
    start_server = input("\n是否启动开发服务器? (y/n): ")
    if start_server.lower() == 'y':
        print("\n启动开发服务器...")
        print("访问 http://127.0.0.1:8000/ 进行测试")
        try:
            subprocess.run(["python", "manage.py", "runserver"], check=True)
        except KeyboardInterrupt:
            print("\n\n服务器已停止")
        except Exception as e:
            print(f"\n启动服务器时出错: {e}")
    
    print_header("部署完成")
    print("\n二维码功能已部署完成!")
    print("\n后续操作:")
    print("1. 检查部署日志")
    print("2. 测试各项功能")
    print("3. 查看QR_CODE_USAGE.md获取详细使用说明")
    print("4. 如有问题，检查错误日志")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断部署")
    except Exception as e:
        print(f"\n部署过程中出错: {e}")
        import traceback
        traceback.print_exc()