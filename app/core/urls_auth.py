from django.urls import path
from core.views_auth import confirm_email, approve_account, register, login, logout

urlpatterns = [
    path('confirm/<str:token>/', confirm_email, name='auth_confirm'),
    path('approve/<str:token>/', approve_account, name='auth_approve'),
    path('register/', register, name='auth_register'),
    path('login/', login, name='auth_login'),
    path('logout/', logout, name='auth_logout'),
]
