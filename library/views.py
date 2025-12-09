# book_management/library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.http import JsonResponse
from .models import Book, BookCopy, User
from django.utils.translation import gettext_lazy as _

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