# library/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': '用户名',
            'password1': '密码',
            'password2': '确认密码',
        }
        help_texts = {
            'username': '请输入您的用户名',
            'password1': '请输入您的密码',
            'password2': '请再次输入您的密码',
        }