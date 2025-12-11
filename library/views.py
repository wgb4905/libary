# book_management/library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.http import JsonResponse
from .models import Book, BookCopy, User
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
import json

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    available_copies_count = book.copies.filter(is_available=True).count()
    user_has_borrowed = False
    if request.user.is_authenticated:
        user_has_borrowed = book.copies.filter(borrower=request.user).exists()
    return render(request, 'library/book_detail.html', {
        'book': book,
        'available_copies_count': available_copies_count,
        'user_has_borrowed': user_has_borrowed
    })

def my_borrowings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    borrowed_copies = BookCopy.objects.filter(borrower=request.user)
    today = timezone.now().date()
    for copy in borrowed_copies:
        if copy.due_date < today:
            copy.status = 'overdue'
            copy.days_overdue = (today - copy.due_date).days
        elif copy.due_date == today:
            copy.status = 'due_today'
        else:
            copy.status = 'not_due'
            copy.days_remaining = (copy.due_date - today).days
    return render(request, 'library/my_borrowings.html', {'borrowed_copies': borrowed_copies, 'today': today})

def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

def borrow_book(request, book_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': '请先登录'})
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        available_copy = book.copies.filter(is_available=True).first()
        if available_copy:
            days = int(request.POST.get('days', 7))
            available_copy.borrower = request.user
            available_copy.borrowed_date = timezone.now()
            available_copy.due_date = timezone.now() + timezone.timedelta(days=days)
            available_copy.is_available = False
            available_copy.save()
            return JsonResponse({
                'success': True,
                'book_title': book.title,
                'book_author': book.author,
                'due_date': available_copy.due_date.strftime('%Y-%m-%d')
            })
    return JsonResponse({'success': False, 'error': '租借失败'})

def return_book(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    borrowed_copy = book.copies.filter(borrower=request.user).first()
    if borrowed_copy:
        borrowed_copy.borrower = None
        borrowed_copy.borrowed_date = None
        borrowed_copy.due_date = None
        borrowed_copy.is_available = True
        borrowed_copy.save()
    return redirect('my_borrowings')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
        return render(request, 'library/login.html', {
            'form': form,
            'error': _('用户名或密码错误'),
            'show_retry': True
        })
    return render(request, 'library/login.html', {'form': AuthenticationForm()})

def user_logout(request):
    logout(request)
    return redirect('book_list')

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

# 检测是否为移动设备
def is_mobile_device(request):
    """检测用户是否使用移动设备访问"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
    
    for keyword in mobile_keywords:
        if keyword in user_agent:
            return True
    return False

# 新增二维码相关功能
def scan_qr_code(request, bookcopy_id):
    """处理二维码扫描请求"""
    book_copy = get_object_or_404(BookCopy, id=bookcopy_id)
    
    # 检测是否为移动设备
    if is_mobile_device(request):
        template_name = 'library/qr_mobile_scan.html'
    else:
        template_name = 'library/qr_scan.html'
    
    if request.method == 'GET':
        # 显示图书信息和借阅状态
        return render(request, template_name, {
            'book_copy': book_copy,
            'book': book_copy.book,
            'is_available': book_copy.is_available,
            'borrower': book_copy.borrower,
            'due_date': book_copy.due_date,
        })
    
    elif request.method == 'POST':
        # 处理借阅/归还操作
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'error': '请先登录',
                'redirect_url': '/login/'
            })
        
        if book_copy.is_available:
            # 借阅图书
            days = int(request.POST.get('days', 7))
            book_copy.borrower = request.user
            book_copy.borrowed_date = timezone.now()
            book_copy.due_date = timezone.now() + timezone.timedelta(days=days)
            book_copy.is_available = False
            book_copy.save()
            
            return JsonResponse({
                'success': True,
                'action': 'borrow',
                'message': f'成功借阅《{book_copy.book.title}》',
                'due_date': book_copy.due_date.strftime('%Y-%m-%d'),
                'book_title': book_copy.book.title,
                'book_author': book_copy.book.author
            })
        else:
            # 检查是否是当前用户借阅的
            if book_copy.borrower == request.user:
                # 归还图书
                book_copy.borrower = None
                book_copy.borrowed_date = None
                book_copy.due_date = None
                book_copy.is_available = True
                book_copy.save()
                
                return JsonResponse({
                    'success': True,
                    'action': 'return',
                    'message': f'成功归还《{book_copy.book.title}》',
                    'book_title': book_copy.book.title,
                    'book_author': book_copy.book.author
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'此书已被{book_copy.borrower.username}借阅，无法归还',
                    'due_date': book_copy.due_date.strftime('%Y-%m-%d') if book_copy.due_date else None
                })

def qr_code_info(request, bookcopy_id):
    """获取图书副本信息的API接口（用于移动端扫描）"""
    book_copy = get_object_or_404(BookCopy, id=bookcopy_id)
    
    data = {
        'id': book_copy.id,
        'book_id': book_copy.book.id,
        'book_title': book_copy.book.title,
        'book_author': book_copy.book.author,
        'is_available': book_copy.is_available,
        'borrower': book_copy.borrower.username if book_copy.borrower else None,
        'due_date': book_copy.due_date.strftime('%Y-%m-%d') if book_copy.due_date else None,
        'borrowed_date': book_copy.borrowed_date.strftime('%Y-%m-%d') if book_copy.borrowed_date else None,
        'qr_code_url': book_copy.qr_code.url if book_copy.qr_code else None,
        'scan_url': request.build_absolute_uri(f'/scan/{book_copy.id}/')
    }
    
    return JsonResponse(data)

def generate_qr_codes(request):
    """为所有没有二维码的图书副本生成二维码（管理功能）"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': '需要登录'})
    
    # 允许超级用户或管理员访问
    if not (request.user.is_superuser or getattr(request.user, 'is_admin', False)):
        return JsonResponse({'success': False, 'error': '需要管理员权限'})
    
    # 支持为单个副本生成二维码
    copy_id = request.POST.get('copy_id')
    if copy_id:
        copy = get_object_or_404(BookCopy, id=copy_id)
        if not copy.qr_code:
            copy.generate_qr_code()
            copy.save()
            return JsonResponse({
                'success': True,
                'message': f'成功为副本 {copy_id} 生成二维码',
                'count': 1
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '该副本已有二维码'
            })
    
    # 批量生成
    copies_without_qr = BookCopy.objects.filter(qr_code='') | BookCopy.objects.filter(qr_code__isnull=True)
    count = 0
    
    for copy in copies_without_qr:
        copy.generate_qr_code()
        copy.save()
        count += 1
    
    return JsonResponse({
        'success': True,
        'message': f'成功为{count}个图书副本生成二维码',
        'count': count
    })

def qr_code_display(request, bookcopy_id):
    """显示图书二维码（用于打印）"""
    book_copy = get_object_or_404(BookCopy, id=bookcopy_id)
    
    return render(request, 'library/qr_display.html', {
        'book_copy': book_copy,
        'book': book_copy.book,
        'qr_code_url': book_copy.qr_code.url if book_copy.qr_code else None,
    })

def qr_management(request, book_id):
    """图书二维码管理页面"""
    # 临时注释掉权限检查进行测试
    # if not request.user.is_authenticated:
    #     return redirect('login')
    # 
    # # 允许超级用户或管理员访问
    # if not (request.user.is_superuser or getattr(request.user, 'is_admin', False)):
    #     return redirect('login')
    
    book = get_object_or_404(Book, id=book_id)
    available_copies_count = book.copies.filter(is_available=True).count()
    
    return render(request, 'library/qr_management.html', {
        'book': book,
        'available_copies_count': available_copies_count,
    })