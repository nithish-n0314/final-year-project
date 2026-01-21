from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Sum
from datetime import datetime, timedelta
import json

from .models import User, Expense, ChatMessage
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    ExpenseSerializer,
    ChatMessageSerializer
)
# Lazy import heavy AI modules inside endpoints to avoid blocking server startup
from .reports import ReportGenerator

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

# User Profile Views
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Expense Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expenses(request):
    """Get user expenses or create new expense"""
    if request.method == 'GET':
        user_expenses = Expense.objects.filter(user=request.user)
        
        # Filter by date range if provided
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            user_expenses = user_expenses.filter(date__gte=start_date)
        if end_date:
            user_expenses = user_expenses.filter(date__lte=end_date)
        
        serializer = ExpenseSerializer(user_expenses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Use AI to categorize if category not provided
            if not serializer.validated_data.get('category'):
                try:
                    from .ai_langchain import FinanceAI
                    ai = FinanceAI()
                    category = ai.categorize_expense(serializer.validated_data['description'])
                except Exception:
                    # Fallback simple categorization if ML libs not available
                    description_lower = serializer.validated_data['description'].lower()
                    if any(word in description_lower for word in ['restaurant', 'food', 'meal', 'lunch', 'dinner', 'breakfast']):
                        category = 'food'
                    elif any(word in description_lower for word in ['uber', 'taxi', 'gas', 'fuel', 'transport']):
                        category = 'transportation'
                    else:
                        category = 'other'
                serializer.validated_data['category'] = category
            
            expense = serializer.save()
            return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf_expenses(request):
    """Upload PDF and extract expenses"""
    try:
        if 'pdf_file' not in request.FILES:
            return Response({'error': 'No PDF file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_file = request.FILES['pdf_file']
        
        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return Response({'error': 'File must be a PDF'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .ai_pdf import PDFExpenseExtractor
            extractor = PDFExpenseExtractor()
            expenses_data = extractor.process_pdf_expenses(pdf_file)
        except Exception as e:
            return Response({'error': f'PDF processing unavailable: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not expenses_data:
            return Response({'error': 'No expenses found in PDF'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create expense objects
        created_expenses = []
        for expense_data in expenses_data:
            expense = Expense.objects.create(
                user=request.user,
                amount=expense_data['amount'],
                description=expense_data['description'],
                category=expense_data['category'],
                date=expense_data['date'],
                is_from_pdf=True
            )
            created_expenses.append(expense)
        
        serializer = ExpenseSerializer(created_expenses, many=True)
        return Response({
            'message': f'Successfully extracted {len(created_expenses)} expenses from PDF',
            'expenses': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Dashboard Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Get dashboard data with insights"""
    try:
        report_generator = ReportGenerator()
        insights = report_generator.get_dashboard_insights(request.user)
        
        # Generate AI suggestions (lazy import)
        try:
            from .ai_langchain import FinanceAI
            ai = FinanceAI()
            savings_suggestions = ai.generate_savings_suggestions(request.user)
            investment_ideas = ai.generate_investment_ideas(request.user)
        except Exception:
            savings_suggestions = []
            investment_ideas = []
        
        return Response({
            'user': UserSerializer(request.user).data,
            'insights': insights,
            'savings_suggestions': savings_suggestions,
            'investment_ideas': investment_ideas
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Chat Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """AI chatbot endpoint"""
    try:
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate AI response (lazy import)
        try:
            from .ai_langchain import FinanceAI
            ai = FinanceAI()
            response = ai.chat_response(request.user, message)
        except Exception:
            response = "AI service unavailable. Please try later."
        
        # Save chat message
        chat_message = ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=response
        )
        
        return Response({
            'message': message,
            'response': response,
            'timestamp': chat_message.created_at
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """Get user's chat history"""
    messages = ChatMessage.objects.filter(user=request.user)[:20]  # Last 20 messages
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

# Report Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """Generate financial report for date range"""
    try:
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Both start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report
        report_generator = ReportGenerator()
        report = report_generator.generate_financial_report(
            request.user, start_date, end_date
        )
        
        return Response(report)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_analytics(request):
    """Get expense analytics data"""
    try:
        # Get date range (default to last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        
        expenses = Expense.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Category breakdown
        category_data = expenses.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        total_expenses = sum(item['total'] for item in category_data)
        
        categories = []
        for item in category_data:
            categories.append({
                'category': item['category'],
                'amount': float(item['total']),
                'percentage': (float(item['total']) / float(total_expenses) * 100) if total_expenses > 0 else 0
            })
        
        return Response({
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'total_expenses': float(total_expenses),
            'categories': categories
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)