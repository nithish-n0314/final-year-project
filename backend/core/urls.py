from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    
    # Expenses
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/upload-pdf/', views.upload_pdf_expenses, name='upload_pdf_expenses'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Chat
    path('chat/', views.chat, name='chat'),
    path('chat/history/', views.chat_history, name='chat_history'),
    
    # Reports
    path('reports/', views.generate_report, name='generate_report'),
    
    # Analytics
    path('analytics/', views.expense_analytics, name='expense_analytics'),
]