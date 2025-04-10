# core/urls_auth.py

from django.urls import path
from . import views_auth

urlpatterns = [
    path('register/', views_auth.register, name='auth_register'),
    path('confirm/<str:token>/', views_auth.confirm_email, name='auth_confirm'),
    path('approve/<str:token>/', views_auth.approve_account, name='auth_approve'),
    path('login/', views_auth.login, name='auth_login'),
    path('logout/', views_auth.logout, name='auth_logout'),
]
