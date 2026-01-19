import os
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from django.conf import settings
from .models import User, Expense, ChatMessage
from datetime import datetime, timedelta
from decimal import Decimal

class FinanceAI:
    def __init__(self):
        self.llm = OpenAI(
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
    
    def categorize_expense(self, description):
        """Categorize expense using LangChain"""
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Categorize the following expense description into one of these categories:
            - food (Food & Dining)
            - transportation (Transportation)
            - shopping (Shopping)
            - entertainment (Entertainment)
            - bills (Bills & Utilities)
            - healthcare (Healthcare)
            - education (Education)
            - travel (Travel)
            - groceries (Groceries)
            - other (Other)
            
            Expense description: {description}
            
            Return only the category name (e.g., 'food', 'transportation', etc.):
            """
        )
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({"description": description}).strip().lower()
        except:
            # Fallback categorization
            description_lower = description.lower()
            if any(word in description_lower for word in ['restaurant', 'food', 'meal', 'lunch', 'dinner', 'breakfast']):
                return 'food'
            elif any(word in description_lower for word in ['uber', 'taxi', 'gas', 'fuel', 'transport']):
                return 'transportation'
            elif any(word in description_lower for word in ['store', 'shopping', 'amazon', 'buy']):
                return 'shopping'
            elif any(word in description_lower for word in ['movie', 'entertainment', 'game', 'concert']):
                return 'entertainment'
            elif any(word in description_lower for word in ['bill', 'utility', 'electric', 'water', 'internet']):
                return 'bills'
            elif any(word in description_lower for word in ['doctor', 'hospital', 'pharmacy', 'medical']):
                return 'healthcare'
            elif any(word in description_lower for word in ['school', 'education', 'course', 'book']):
                return 'education'
            elif any(word in description_lower for word in ['hotel', 'flight', 'travel', 'vacation']):
                return 'travel'
            elif any(word in description_lower for word in ['grocery', 'supermarket', 'walmart', 'target']):
                return 'groceries'
            else:
                return 'other'
        
        # Validate category
        valid_categories = ['food', 'transportation', 'shopping', 'entertainment', 
                          'bills', 'healthcare', 'education', 'travel', 'groceries', 'other']
        
        return result if result in valid_categories else 'other'
    
    def generate_savings_suggestions(self, user):
        """Generate personalized savings suggestions using LangChain"""
        # Get user's recent expenses
        recent_expenses = Expense.objects.filter(
            user=user,
            date__gte=datetime.now().date() - timedelta(days=30)
        )
        
        total_expenses = sum(expense.amount for expense in recent_expenses)
        expense_categories = {}
        
        for expense in recent_expenses:
            if expense.category in expense_categories:
                expense_categories[expense.category] += expense.amount
            else:
                expense_categories[expense.category] = expense.amount
        
        # Create context for AI
        expense_summary = ", ".join([f"{cat}: ₹{amount}" for cat, amount in expense_categories.items()])
        
        prompt = PromptTemplate(
            input_variables=["role", "monthly_income", "total_expenses", "expense_summary"],
            template="""
            You are a financial advisor. Generate 3 personalized savings suggestions for a {role}.
            
            User Profile:
            - Role: {role}
            - Monthly Income: {monthly_income}
            - Total Monthly Expenses: ₹{total_expenses}
            - Expense Breakdown: {expense_summary}
            
            Provide 3 specific, actionable savings suggestions. Each suggestion should be:
            1. Practical and achievable
            2. Tailored to their role and spending pattern
            3. Include estimated savings amount
            
            Format as a JSON array of objects with 'title', 'description', and 'estimated_savings' fields:
            """
        )
        
        income_text = f"${user.monthly_income}" if user.monthly_income else "Not specified (Student)"
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({
                "role": user.role,
                "monthly_income": income_text,
                "total_expenses": total_expenses,
                "expense_summary": expense_summary or "No recent expenses"
            })
            
            import json
            suggestions = json.loads(result)
            return suggestions[:3]  # Ensure max 3 suggestions
        except Exception as e:
            print(f"OpenAI savings suggestions failed: {e}")
            return self._generate_salary_based_suggestions(user, expense_categories, total_expenses)
    
    def _generate_salary_based_suggestions(self, user, expense_categories, total_expenses):
        """Generate strictly salary-based personalized recommendations"""
        monthly_income = float(user.monthly_income) if user.monthly_income else 0
        
        # MANDATORY salary classification for personalization
        if monthly_income == 0:
            income_level = "student"
            affordability_range = "under ₹4,000"
            savings_capacity = 25
        elif monthly_income < 3000:
            income_level = "entry"
            affordability_range = "₹4,000-16,000"
            savings_capacity = monthly_income * 0.15
        elif monthly_income < 6000:
            income_level = "mid"
            affordability_range = "₹16,000-40,000"
            savings_capacity = monthly_income * 0.20
        elif monthly_income < 10000:
            income_level = "high"
            affordability_range = "₹40,000-80,000"
            savings_capacity = monthly_income * 0.25
        else:
            income_level = "premium"
            affordability_range = "₹80,000+"
            savings_capacity = monthly_income * 0.30
        
        # Calculate current financial health
        spending_ratio = (float(total_expenses) / monthly_income * 100) if monthly_income > 0 else 0
        
        # SALARY-SPECIFIC recommendations (MUST be different for different salaries)
        if income_level == "student":
            return [
                {
                    "title": "Micro-Savings for Students",
                    "description": f"Save ₹80-160 daily from your limited budget. Achievable within your {affordability_range} capacity.",
                    "estimated_savings": "₹2,400-4,800/month",
                    "affordability_explanation": f"Designed for {affordability_range} student budget - no income pressure"
                },
                {
                    "title": "Free Resource Maximization",
                    "description": f"Use free campus resources, student discounts. Perfect for {affordability_range} spending power.",
                    "estimated_savings": "₹1,600-3,200/month",
                    "affordability_explanation": f"Zero cost strategy fitting {affordability_range} constraints"
                },
                {
                    "title": "Skill Investment Priority",
                    "description": f"Invest in future earning potential. Small investments within {affordability_range} for big returns.",
                    "estimated_savings": "Future income boost",
                    "affordability_explanation": f"Low-cost, high-impact within {affordability_range}"
                }
            ]
        
        elif income_level == "entry":  # Under ₹2,50,000
            return [
                {
                    "title": f"Entry-Level Auto-Save (₹{monthly_income:.0f} income)",
                    "description": f"Auto-save ₹{savings_capacity:.0f}/month (15% of ₹{monthly_income:.0f}). Perfectly calibrated for your {affordability_range} bracket.",
                    "estimated_savings": f"₹{savings_capacity:.0f}/month",
                    "affordability_explanation": f"Conservative 15% rate suitable for {affordability_range} income level"
                },
                {
                    "title": f"Budget Optimization (₹{monthly_income:.0f} earner)",
                    "description": f"With ₹{monthly_income:.0f}/month, focus on essentials. Target {affordability_range} monthly savings through smart cuts.",
                    "estimated_savings": f"₹{monthly_income*0.10:.0f}-{monthly_income*0.15:.0f}",
                    "affordability_explanation": f"Realistic targets for {affordability_range} income bracket"
                },
                {
                    "title": f"Career Investment (₹{monthly_income:.0f} salary)",
                    "description": f"Invest ₹{monthly_income*0.05:.0f}/month in skills. Your {affordability_range} income can support strategic career moves.",
                    "estimated_savings": "20-50% salary increase potential",
                    "affordability_explanation": f"Affordable career investment within {affordability_range} means"
                }
            ]
        
        elif income_level == "mid":  # ₹2,50,000-5,00,000
            return [
                {
                    "title": f"Mid-Income Wealth Building (₹{monthly_income:.0f})",
                    "description": f"Save ₹{savings_capacity:.0f}/month (20% of ₹{monthly_income:.0f}). Your {affordability_range} income enables solid wealth building.",
                    "estimated_savings": f"₹{savings_capacity:.0f}/month",
                    "affordability_explanation": f"Standard 20% rule perfect for {affordability_range} earners"
                },
                {
                    "title": f"Strategic Lifestyle Upgrade (₹{monthly_income:.0f})",
                    "description": f"Invest ₹{monthly_income*0.15:.0f}/month in efficiency gains. Your {affordability_range} bracket supports smart upgrades.",
                    "estimated_savings": f"₹{monthly_income*0.10:.0f}-{monthly_income*0.20:.0f}",
                    "affordability_explanation": f"ROI-focused spending within {affordability_range} capacity"
                },
                {
                    "title": f"Investment Portfolio Start (₹{monthly_income:.0f})",
                    "description": f"Begin with ₹{monthly_income*0.10:.0f}/month investing. Your {affordability_range} income supports market entry.",
                    "estimated_savings": "7-10% annual returns",
                    "affordability_explanation": f"Conservative start appropriate for {affordability_range} income"
                }
            ]
        
        elif income_level == "high":  # ₹5,00,000-8,00,000
            return [
                {
                    "title": f"High-Income Acceleration (₹{monthly_income:.0f})",
                    "description": f"Aggressive save ₹{savings_capacity:.0f}/month (25% of ₹{monthly_income:.0f}). Your {affordability_range} income enables rapid wealth building.",
                    "estimated_savings": f"₹{savings_capacity:.0f}/month",
                    "affordability_explanation": f"Aggressive but sustainable for {affordability_range} earners"
                },
                {
                    "title": f"Tax Optimization Strategy (₹{monthly_income:.0f})",
                    "description": f"Max retirement contributions: ₹{monthly_income*0.20:.0f}/month. Your {affordability_range} bracket benefits from tax strategies.",
                    "estimated_savings": f"₹{monthly_income*0.25:.0f}/month tax savings",
                    "affordability_explanation": f"High-value tax moves for {affordability_range} income"
                },
                {
                    "title": f"Diversified Investment (₹{monthly_income:.0f})",
                    "description": f"Invest ₹{monthly_income*0.15:.0f}/month across assets. Your {affordability_range} income supports diversification.",
                    "estimated_savings": "8-12% annual returns",
                    "affordability_explanation": f"Advanced strategies fitting {affordability_range} capacity"
                }
            ]
        
        else:  # Premium ₹8,00,000+
            return [
                {
                    "title": f"Premium Wealth Strategy (₹{monthly_income:.0f})",
                    "description": f"Elite save ₹{savings_capacity:.0f}/month (30% of ₹{monthly_income:.0f}). Your {affordability_range} income enables premium strategies.",
                    "estimated_savings": f"₹{savings_capacity:.0f}/month",
                    "affordability_explanation": f"Elite savings rate for {affordability_range} high earners"
                },
                {
                    "title": f"Advanced Tax & Estate Planning (₹{monthly_income:.0f})",
                    "description": f"Professional services worth ₹{monthly_income*0.02:.0f}/month. Your {affordability_range} income justifies premium advice.",
                    "estimated_savings": f"₹{monthly_income*0.15:.0f}/month tax optimization",
                    "affordability_explanation": f"High-value professional services for {affordability_range} earners"
                },
                {
                    "title": f"Alternative Investment Access (₹{monthly_income:.0f})",
                    "description": f"Real estate, private equity: ₹{monthly_income*0.20:.0f}/month. Your {affordability_range} income opens exclusive opportunities.",
                    "estimated_savings": "12-20% annual returns",
                    "affordability_explanation": f"Exclusive investments available to {affordability_range} income bracket"
                }
            ]
    
    def generate_investment_ideas(self, user):
        """Generate personalized investment ideas using LangChain"""
        prompt = PromptTemplate(
            input_variables=["role", "monthly_income"],
            template="""
            You are a financial advisor. Generate 3 safe, educational investment ideas for a {role}.
            
            User Profile:
            - Role: {role}
            - Monthly Income: {monthly_income}
            
            Provide 3 investment suggestions that are:
            1. Educational and beginner-friendly
            2. Low to moderate risk
            3. Appropriate for their role and income level
            4. Include risk explanation
            
            Format as a JSON array of objects with 'title', 'description', 'risk_level', and 'min_investment' fields:
            """
        )
        
        income_text = f"₹{user.monthly_income}" if user.monthly_income else "Not specified (Student)"
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({
                "role": user.role,
                "monthly_income": income_text
            })
            
            import json
            ideas = json.loads(result)
            return ideas[:3]  # Ensure max 3 ideas
        except Exception as e:
            print(f"OpenAI investment ideas failed: {e}")
            return self._generate_salary_based_investments(user)
    
    def _generate_salary_based_investments(self, user):
        """Generate salary-specific investment recommendations"""
        monthly_income = float(user.monthly_income) if user.monthly_income else 0
        
        # Classify income for investment capacity
        if monthly_income == 0:
            investment_capacity = 25
            risk_tolerance = "Very Low"
            affordability = "under $50"
        elif monthly_income < 3000:
            investment_capacity = monthly_income * 0.10
            risk_tolerance = "Low"
            affordability = "$50-300"
        elif monthly_income < 6000:
            investment_capacity = monthly_income * 0.15
            risk_tolerance = "Low to Moderate"
            affordability = "₹25,000-75,000"
        elif monthly_income < 10000:
            investment_capacity = monthly_income * 0.20
            risk_tolerance = "Moderate"
            affordability = "₹75,000-1,60,000"
        else:
            investment_capacity = monthly_income * 0.25
            risk_tolerance = "Moderate to High"
            affordability = "₹1,60,000+"
        
        # SALARY-SPECIFIC investment recommendations
        if monthly_income == 0:  # Student
            return [
                {
                    "title": "Student Investment Start",
                    "description": f"Begin with ₹{investment_capacity:.0f}/month in high-yield savings. Perfect for your {affordability} budget.",
                    "risk_level": risk_tolerance,
                    "min_investment": f"₹{investment_capacity:.0f}",
                    "affordability_explanation": f"Designed for {affordability} student capacity"
                },
                {
                    "title": "Education ROI Focus",
                    "description": f"Invest in skills/certifications within {affordability} range. Highest ROI for students.",
                    "risk_level": "No Risk",
                    "min_investment": "₹2,000-4,000",
                    "affordability_explanation": f"Career investment within {affordability} means"
                },
                {
                    "title": "Micro-Investment Apps",
                    "description": f"Use spare change apps. Start with ₹{investment_capacity/5:.0f}/month within {affordability} budget.",
                    "risk_level": risk_tolerance,
                    "min_investment": "₹400-800",
                    "affordability_explanation": f"Micro-amounts perfect for {affordability} budget"
                }
            ]
        
        elif monthly_income < 3000:  # Entry level
            return [
                {
                    "title": f"Entry-Level Portfolio (₹{monthly_income:.0f} income)",
                    "description": f"Invest ₹{investment_capacity:.0f}/month (10% of income) in index funds. Suitable for {affordability} bracket.",
                    "risk_level": risk_tolerance,
                    "min_investment": f"₹{investment_capacity:.0f}",
                    "affordability_explanation": f"Conservative 10% allocation for {affordability} earners"
                },
                {
                    "title": f"Emergency Fund Priority (₹{monthly_income:.0f})",
                    "description": f"Build ₹{monthly_income*3:.0f} emergency fund first. Critical for {affordability} income stability.",
                    "risk_level": "Very Low",
                    "min_investment": f"₹{monthly_income*0.15:.0f}/month",
                    "affordability_explanation": f"Essential safety net for {affordability} income level"
                },
                {
                    "title": f"Employer Match Focus (₹{monthly_income:.0f})",
                    "description": f"Maximize EPF match if available. Free money for {affordability} earners.",
                    "risk_level": "Low",
                    "min_investment": "Employer dependent",
                    "affordability_explanation": f"Prioritize free money within {affordability} means"
                }
            ]
        
        elif monthly_income < 6000:  # Mid-income
            return [
                {
                    "title": f"Balanced Portfolio (₹{monthly_income:.0f} income)",
                    "description": f"Invest ₹{investment_capacity:.0f}/month (15% of income) across stocks/bonds. Perfect for {affordability} bracket.",
                    "risk_level": risk_tolerance,
                    "min_investment": f"₹{investment_capacity:.0f}",
                    "affordability_explanation": f"Balanced approach for {affordability} income level"
                },
                {
                    "title": f"Tax-Advantaged Accounts (₹{monthly_income:.0f})",
                    "description": f"Max ELSS contributions: ₹{min(12500, investment_capacity):.0f}/month. Tax benefits for {affordability} earners.",
                    "risk_level": "Low to Moderate",
                    "min_investment": f"₹{min(12500, investment_capacity):.0f}",
                    "affordability_explanation": f"Tax optimization within {affordability} capacity"
                },
                {
                    "title": f"Real Estate Start (₹{monthly_income:.0f})",
                    "description": f"Consider REITs with ₹{investment_capacity*0.3:.0f}/month. Real estate exposure for {affordability} income.",
                    "risk_level": "Moderate",
                    "min_investment": f"₹{investment_capacity*0.3:.0f}",
                    "affordability_explanation": f"Real estate access for {affordability} bracket"
                }
            ]
        
        elif monthly_income < 10000:  # High income
            return [
                {
                    "title": f"Aggressive Growth (₹{monthly_income:.0f} income)",
                    "description": f"Invest ₹{investment_capacity:.0f}/month (20% of income) in growth stocks. Your {affordability} income supports higher risk.",
                    "risk_level": risk_tolerance,
                    "min_investment": f"₹{investment_capacity:.0f}",
                    "affordability_explanation": f"Growth focus appropriate for {affordability} earners"
                },
                {
                    "title": f"Diversified Strategy (₹{monthly_income:.0f})",
                    "description": f"Split ₹{investment_capacity:.0f}/month across multiple asset classes. {affordability} income enables diversification.",
                    "risk_level": "Moderate",
                    "min_investment": f"₹{investment_capacity*0.25:.0f} per asset",
                    "affordability_explanation": f"Multi-asset approach for {affordability} bracket"
                },
                {
                    "title": f"Alternative Investments (₹{monthly_income:.0f})",
                    "description": f"Explore commodities, crypto with ₹{investment_capacity*0.1:.0f}/month. {affordability} income allows alternatives.",
                    "risk_level": "High",
                    "min_investment": f"₹{investment_capacity*0.1:.0f}",
                    "affordability_explanation": f"Alternative access for {affordability} income level"
                }
            ]
        
        else:  # Premium income
            return [
                {
                    "title": f"Elite Investment Strategy (₹{monthly_income:.0f})",
                    "description": f"Invest ₹{investment_capacity:.0f}/month (25% of income) in premium opportunities. {affordability} income opens elite options.",
                    "risk_level": risk_tolerance,
                    "min_investment": f"₹{investment_capacity:.0f}",
                    "affordability_explanation": f"Premium strategies for {affordability} high earners"
                },
                {
                    "title": f"Private Equity Access (₹{monthly_income:.0f})",
                    "description": f"Minimum ₹{investment_capacity*0.5:.0f}/month for private investments. {affordability} income qualifies for exclusive deals.",
                    "risk_level": "Moderate to High",
                    "min_investment": f"₹{investment_capacity*0.5:.0f}",
                    "affordability_explanation": f"Exclusive access for {affordability} earners"
                },
                {
                    "title": f"Tax Optimization Complex (₹{monthly_income:.0f})",
                    "description": f"Advanced tax strategies worth ₹{monthly_income*0.02:.0f}/month in fees. {affordability} income justifies complexity.",
                    "risk_level": "Low",
                    "min_investment": f"₹{investment_capacity*0.8:.0f}",
                    "affordability_explanation": f"Advanced planning for {affordability} income bracket"
                }
            ]
    
    def chat_response(self, user, message):
        """Generate chatbot response using LangChain"""
        # Get user context
        recent_expenses = Expense.objects.filter(
            user=user,
            date__gte=datetime.now().date() - timedelta(days=30)
        )
        
        total_expenses = sum(expense.amount for expense in recent_expenses)
        expense_count = recent_expenses.count()
        
        prompt = PromptTemplate(
            input_variables=["role", "monthly_income", "message", "total_expenses", "expense_count"],
            template="""
            You are a helpful personal finance assistant. Answer the user's question based on their profile and spending data.
            
            User Profile:
            - Role: {role}
            - Monthly Income: {monthly_income}
            - Recent Monthly Expenses: ₹{total_expenses}
            - Number of Recent Transactions: {expense_count}
            
            User Question: {message}
            
            Provide a helpful, personalized response. Be encouraging and practical. Keep it concise but informative:
            """
        )
        
        income_text = f"${user.monthly_income}" if user.monthly_income else "Not specified (Student)"
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "role": user.role,
                "monthly_income": income_text,
                "message": message,
                "total_expenses": total_expenses,
                "expense_count": expense_count
            })
            return response.strip()
        except Exception as e:
            print(f"OpenAI chat response failed: {e}")
            try:
                return self._generate_personalized_response(user, message, total_expenses, expense_count)
            except Exception as fallback_error:
                print(f"Fallback response failed: {fallback_error}")
                # Ultimate fallback - simple but functional response
                return f"Hi {user.username}! I'm here to help with your finances. As a {user.role}, I can assist you with budgeting, saving tips, and investment advice. What would you like to know about your financial situation?"
    
    def _generate_personalized_response(self, user, message, total_expenses, expense_count):
        """Generate personalized chat responses with context awareness and anti-repetition"""
        message_lower = message.lower()
        monthly_income = float(user.monthly_income) if user.monthly_income else 0
        
        # Get user's recent chat history to avoid repetition
        recent_chats = ChatMessage.objects.filter(user=user).order_by('-created_at')[:5]
        previous_topics = [chat.message.lower() for chat in recent_chats]
        
        # Personalization based on user context
        name_greeting = f"{user.username}, " if len(user.username) < 15 else ""
        
        # Income-based personalization
        if monthly_income == 0:
            income_context = "as a student with flexible income"
            affordability = "budget-friendly"
        elif monthly_income < 3000:
            income_context = f"with your ₹{monthly_income:.0f}/month income"
            affordability = "cost-effective"
        elif monthly_income < 6000:
            income_context = f"earning ₹{monthly_income:.0f} monthly"
            affordability = "moderate-budget"
        else:
            income_context = f"with your ₹{monthly_income:.0f} monthly earnings"
            affordability = "higher-end"
        
        # Anti-repetition: Check if user asked similar questions before
        asked_savings_before = any('save' in topic or 'saving' in topic for topic in previous_topics)
        asked_investment_before = any('invest' in topic for topic in previous_topics)
        asked_spending_before = any('spend' in topic or 'budget' in topic for topic in previous_topics)
        
        # Savings-related questions with personalization and anti-repetition
        if any(word in message_lower for word in ['save', 'saving', 'savings']):
            if asked_savings_before:
                # Different approach for repeat questions
                if user.role == 'student':
                    return f"Since we talked about saving before, {name_greeting}let me give you a fresh angle. Try the 'pay yourself first' method - even ₹1,600 weekly builds momentum. Your student lifestyle actually gives you flexibility most adults don't have."
                else:
                    return f"Building on our previous savings discussion, {name_greeting}consider the 1% rule: increase your savings rate by just 1% each month. {income_context}, this could mean an extra ₹{monthly_income*0.01:.0f} this month, growing to ₹{monthly_income*0.12:.0f} by year-end."
            else:
                # First time savings question
                if user.role == 'student':
                    return f"Great question about savings! {income_context}, I'd suggest starting micro - save your daily coffee money or round up purchases. You've spent ₹{total_expenses:.2f} recently, so even saving 10% of that would be ₹{total_expenses*0.1:.2f}."
                elif monthly_income > 0:
                    savings_target = monthly_income * 0.20
                    return f"{name_greeting}with ₹{total_expenses:.2f} in recent expenses and {income_context}, aim for the 50/30/20 rule. That means ₹{savings_target:.0f}/month in savings - very doable with {affordability} adjustments."
        
        # Investment questions with experience-level adaptation
        elif any(word in message_lower for word in ['invest', 'investment', 'investing']):
            if asked_investment_before:
                # Advanced follow-up for repeat questions
                if monthly_income > 6000:
                    return f"Since you're interested in diving deeper into investing, {name_greeting}let's talk tax-advantaged strategies. {income_context}, you could benefit from maxing out your EPF (₹{monthly_income*0.15:.0f}/month) before taxable investments."
                else:
                    return f"Following up on investments - {name_greeting}have you considered rupee-cost averaging? {income_context}, investing ₹{monthly_income*0.10:.0f} monthly regardless of market conditions reduces timing risk."
            else:
                # First investment discussion
                if user.role == 'student':
                    return f"Smart thinking about investing early! {name_greeting}your biggest investment right now should be in yourself - skills, education, networking. For actual investing, start with {affordability} index funds once you have $500-1000 saved."
                elif monthly_income > 0:
                    investment_amount = monthly_income * 0.15
                    return f"Perfect timing to discuss investing! {income_context}, you could comfortably invest ₹{investment_amount:.0f}/month. Start with broad market index funds - they're {affordability} and diversified."
        
        # Spending analysis with personalized insights
        elif any(word in message_lower for word in ['spending', 'spend', 'expenses', 'budget']):
            if asked_spending_before:
                # Different angle for repeat spending questions
                spending_ratio = (total_expenses / monthly_income * 100) if monthly_income > 0 else 0
                if spending_ratio > 70:
                    return f"Looking at your spending from a new angle, {name_greeting}you're using {spending_ratio:.0f}% of income on expenses. Try the 'envelope method' - allocate specific amounts for each category and stick to them."
                else:
                    return f"Your spending discipline looks solid, {name_greeting}but let's optimize further. {income_context}, focus on your top 3 expense categories - that's where small changes create big impact."
            else:
                # First spending analysis
                if expense_count > 0:
                    avg_expense = total_expenses / expense_count
                    if monthly_income > 0:
                        spending_ratio = total_expenses / monthly_income * 100
                        return f"Let me break down your spending, {name_greeting}. You've had {expense_count} transactions totaling ${total_expenses:.2f} (${avg_expense:.2f} average). That's {spending_ratio:.0f}% of your {income_context} - {'quite manageable' if spending_ratio < 60 else 'worth optimizing'}."
                    else:
                        return f"Looking at your {expense_count} recent transactions totaling ${total_expenses:.2f}, {name_greeting}your average spend is ${avg_expense:.2f}. {income_context}, focus on tracking patterns rather than strict limits."
        
        # Overspending concerns with role-specific advice
        elif any(word in message_lower for word in ['overspend', 'too much', 'control', 'help']):
            if monthly_income > 0:
                if total_expenses > monthly_income * 0.8:
                    return f"I understand the concern, {name_greeting}. Spending ₹{total_expenses:.2f} against {income_context} is indeed high. Let's tackle this systematically - start by cutting your largest expense category by 20%."
                else:
                    return f"Actually, {name_greeting}your spending looks reasonable {income_context}. Sometimes we feel like we're overspending when we're not tracking properly. Your ₹{total_expenses:.2f} recent expenses seem well within your {affordability} range."
            else:
                return f"Feeling overwhelmed by spending is normal, {name_greeting}. {income_context}, focus on needs vs wants. Create a simple rule: wait 24 hours before any non-essential purchase over ₹1,600."
        
        # Emergency fund questions
        elif any(word in message_lower for word in ['emergency', 'fund', 'safety']):
            if monthly_income > 0:
                target_emergency = monthly_income * 3
                monthly_save = monthly_income * 0.10
                return f"Emergency funds are crucial, {name_greeting}! {income_context}, aim for ₹{target_emergency:.0f} (3 months expenses). Save ₹{monthly_save:.0f}/month and you'll reach this {affordability} goal in {target_emergency/monthly_save:.0f} months."
            else:
                return f"Great question about emergency funds! {income_context}, start with a ₹40,000 goal - it covers most unexpected expenses. Even ₹2,000/month gets you there in 20 months, which is very {affordability}."
        
        # Default personalized response with anti-repetition
        else:
            conversation_starters = [
                f"I'm here to help with your financial journey, {name_greeting}! {income_context}, what specific area interests you most?",
                f"Thanks for reaching out! {name_greeting}Given your {user.role} role and {income_context}, I can offer targeted advice on saving, investing, or budgeting.",
                f"Happy to assist, {name_greeting}! With {expense_count} recent transactions and {income_context}, there's lots we can explore together.",
                f"What's on your mind financially, {name_greeting}? {income_context}, I can help you tackle any money challenge - from daily budgeting to long-term wealth building."
            ]
            
            # Avoid repeating the same default response
            used_defaults = [chat.response for chat in recent_chats if any(starter[:20] in chat.response for starter in conversation_starters)]
            available_responses = [resp for resp in conversation_starters if not any(resp[:20] in used for used in used_defaults)]
            
            if available_responses:
                return available_responses[0]
            else:
                return f"Let's dive into your finances, {name_greeting}! {income_context}, whether it's optimizing your budget, planning investments, or building savings - I'm here to provide personalized guidance."
    
    def generate_report_summary(self, user, start_date, end_date, report_data):
        """Generate AI summary for financial report using LangChain"""
        prompt = PromptTemplate(
            input_variables=["role", "start_date", "end_date", "total_expenses", "category_breakdown", "transaction_count"],
            template="""
            Generate a comprehensive financial report summary for a {role}.
            
            Report Period: {start_date} to {end_date}
            Total Expenses: ${total_expenses}
            Number of Transactions: {transaction_count}
            Category Breakdown: {category_breakdown}
            
            Provide a detailed analysis including:
            1. Spending overview
            2. Top spending categories
            3. Spending patterns and insights
            4. Recommendations for improvement
            
            Keep it professional but friendly:
            """
        )
        
        category_text = ", ".join([f"{cat}: ${amount}" for cat, amount in report_data['category_breakdown'].items()])
        
        try:
            chain = prompt | self.llm
            summary = chain.invoke({
                "role": user.role,
                "start_date": start_date,
                "end_date": end_date,
                "total_expenses": report_data['total_expenses'],
                "category_breakdown": category_text,
                "transaction_count": report_data['transaction_count']
            })
            return summary.strip()
        except:
            return f"Financial Report Summary: During the period from {start_date} to {end_date}, you had {report_data['transaction_count']} transactions totaling ${report_data['total_expenses']}. Focus on tracking your spending patterns and consider areas where you can optimize your expenses."