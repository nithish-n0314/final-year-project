from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import Expense
from .ai_langchain import FinanceAI

class ReportGenerator:
    def __init__(self):
        self.ai = FinanceAI()
    
    def generate_financial_report(self, user, start_date, end_date):
        """Generate comprehensive financial report for user"""
        try:
            # Parse dates
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Get expenses in date range
            expenses = Expense.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Calculate totals
            total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
            transaction_count = expenses.count()
            
            # Category breakdown
            category_breakdown = {}
            category_data = expenses.values('category').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            for item in category_data:
                category_breakdown[item['category']] = {
                    'amount': float(item['total']),
                    'count': item['count'],
                    'percentage': (float(item['total']) / float(total_expenses) * 100) if total_expenses > 0 else 0
                }
            
            # Daily spending pattern
            daily_spending = {}
            daily_data = expenses.values('date').annotate(
                total=Sum('amount')
            ).order_by('date')
            
            for item in daily_data:
                daily_spending[item['date'].strftime('%Y-%m-%d')] = float(item['total'])
            
            # Average daily spending
            days_in_period = (end_date - start_date).days + 1
            avg_daily_spending = float(total_expenses) / days_in_period if days_in_period > 0 else 0
            
            # Top expenses
            top_expenses = list(expenses.order_by('-amount')[:10].values(
                'description', 'amount', 'category', 'date'
            ))
            
            # Convert Decimal to float for JSON serialization
            for expense in top_expenses:
                expense['amount'] = float(expense['amount'])
                expense['date'] = expense['date'].strftime('%Y-%m-%d')
            
            # Spending trends (compare with previous period)
            previous_start = start_date - timedelta(days=(end_date - start_date).days + 1)
            previous_end = start_date - timedelta(days=1)
            
            previous_expenses = Expense.objects.filter(
                user=user,
                date__gte=previous_start,
                date__lte=previous_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            spending_change = 0
            if previous_expenses > 0:
                spending_change = ((float(total_expenses) - float(previous_expenses)) / float(previous_expenses)) * 100
            
            # Compile report data
            report_data = {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days_in_period
                },
                'summary': {
                    'total_expenses': float(total_expenses),
                    'transaction_count': transaction_count,
                    'avg_daily_spending': round(avg_daily_spending, 2),
                    'spending_change_percentage': round(spending_change, 2)
                },
                'category_breakdown': category_breakdown,
                'daily_spending': daily_spending,
                'top_expenses': top_expenses,
                'user_profile': {
                    'role': user.role,
                    'monthly_income': float(user.monthly_income) if user.monthly_income else None
                }
            }
            
            # Generate AI summary
            ai_summary = self.ai.generate_report_summary(
                user, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d'),
                {
                    'total_expenses': float(total_expenses),
                    'category_breakdown': {k: v['amount'] for k, v in category_breakdown.items()},
                    'transaction_count': transaction_count
                }
            )
            
            report_data['ai_summary'] = ai_summary
            
            return report_data
            
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")
    
    def get_dashboard_insights(self, user):
        """Generate insights for dashboard"""
        try:
            # Get current month expenses
            now = datetime.now()
            start_of_month = now.replace(day=1).date()
            
            current_month_expenses = Expense.objects.filter(
                user=user,
                date__gte=start_of_month
            )
            
            total_this_month = current_month_expenses.aggregate(total=Sum('amount'))['total'] or 0
            
            # Category breakdown for current month
            category_data = current_month_expenses.values('category').annotate(
                total=Sum('amount')
            ).order_by('-total')
            
            categories = []
            for item in category_data:
                categories.append({
                    'category': item['category'],
                    'amount': float(item['total']),
                    'percentage': (float(item['total']) / float(total_this_month) * 100) if total_this_month > 0 else 0
                })
            
            # Recent transactions
            recent_transactions = list(current_month_expenses.order_by('-date', '-created_at')[:5].values(
                'description', 'amount', 'category', 'date'
            ))
            
            for transaction in recent_transactions:
                transaction['amount'] = float(transaction['amount'])
                transaction['date'] = transaction['date'].strftime('%Y-%m-%d')
            
            # Budget analysis (if user has income)
            budget_analysis = None
            if user.monthly_income:
                remaining_budget = float(user.monthly_income) - float(total_this_month)
                budget_percentage = (float(total_this_month) / float(user.monthly_income)) * 100
                
                budget_analysis = {
                    'monthly_income': float(user.monthly_income),
                    'spent_this_month': float(total_this_month),
                    'remaining_budget': remaining_budget,
                    'budget_percentage': round(budget_percentage, 2),
                    'is_over_budget': remaining_budget < 0
                }
            
            return {
                'total_this_month': float(total_this_month),
                'categories': categories,
                'recent_transactions': recent_transactions,
                'budget_analysis': budget_analysis,
                'transaction_count': current_month_expenses.count()
            }
            
        except Exception as e:
            raise Exception(f"Error generating dashboard insights: {str(e)}")