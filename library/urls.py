# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('book/<int:book_id>/return/', views.return_book, name='return_book'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    # 新增二维码相关路由
    path('scan/<int:bookcopy_id>/', views.scan_qr_code, name='scan_qr_code'),
    path('api/qr-info/<int:bookcopy_id>/', views.qr_code_info, name='qr_code_info'),
    path('admin/generate-qr-codes/', views.generate_qr_codes, name='generate_qr_codes'),
    path('qr/print/<int:bookcopy_id>/', views.qr_code_display, name='qr_code_display'),
    path('book/<int:book_id>/qr-management/', views.qr_management, name='qr_management'),
]