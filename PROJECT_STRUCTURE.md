# Project Structure

## Overview
```
ai app/
├── backend/                    # Django REST API Backend
│   ├── finance_assistant/      # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py         # Django configuration
│   │   ├── urls.py            # Main URL routing
│   │   └── wsgi.py            # WSGI configuration
│   ├── core/                  # Main Django app
│   │   ├── __init__.py
│   │   ├── models.py          # Database models (User, Expense, ChatMessage)
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API endpoints
│   │   ├── urls.py            # App URL routing
│   │   ├── ai_langchain.py    # LangChain AI logic
│   │   ├── ai_pdf.py          # Hugging Face PDF processing
│   │   ├── reports.py         # Report generation logic
│   │   ├── apps.py            # App configuration
│   │   └── admin.py           # Admin (disabled)
│   ├── requirements.txt       # Python dependencies
│   ├── manage.py              # Django management script
│   ├── .env.example           # Environment variables template
│   └── .env                   # Environment variables (created during setup)
├── frontend/                  # React Frontend
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Login.js       # Login page
│   │   │   ├── Register.js    # Registration page
│   │   │   ├── Dashboard.js   # Main dashboard
│   │   │   ├── Navbar.js      # Navigation bar
│   │   │   ├── IncomeInput.js # Income management
│   │   │   ├── ExpenseForm.js # Expense entry & PDF upload
│   │   │   ├── ExpenseChart.js# Chart.js visualizations
│   │   │   ├── SuggestionCards.js # AI suggestions display
│   │   │   ├── ChatBot.js     # AI chatbot interface
│   │   │   └── ReportGenerator.js # Report generation
│   │   ├── context/
│   │   │   └── AuthContext.js # Authentication context
│   │   ├── services/
│   │   │   └── api.js         # Axios API client
│   │   ├── App.js             # Main app component
│   │   ├── index.js           # React entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node.js dependencies
│   └── package-lock.json      # Dependency lock file
├── setup.py                   # Automated setup script
├── start-backend.bat/.sh      # Backend startup scripts
├── start-frontend.bat/.sh     # Frontend startup scripts
├── PROJECT_STRUCTURE.md       # This file
└── README.md                  # Main documentation
```

## Key Components

### Backend Architecture

#### Models (`core/models.py`)
- **User**: Extended Django user with role and monthly_income
- **Expense**: User expenses with AI categorization
- **ChatMessage**: Chat history storage

#### AI Integration
- **ai_langchain.py**: All LangChain reasoning logic
  - Expense categorization
  - Savings suggestions
  - Investment ideas
  - Chatbot responses
  - Report summaries
- **ai_pdf.py**: Hugging Face sentence embeddings for PDF processing

#### API Endpoints (`core/views.py`)
- Authentication: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/`
- Profile: `/api/profile/`
- Expenses: `/api/expenses/`, `/api/expenses/upload-pdf/`
- Dashboard: `/api/dashboard/`
- Chat: `/api/chat/`, `/api/chat/history/`
- Reports: `/api/reports/`
- Analytics: `/api/analytics/`

### Frontend Architecture

#### Components Structure
- **Authentication**: Login/Register with JWT handling
- **Dashboard**: Main interface with all features
- **Expense Management**: Manual entry + PDF upload
- **Visualizations**: Chart.js pie charts and analytics
- **AI Features**: Suggestions cards and chatbot
- **Reports**: Date-range reports with AI summaries

#### State Management
- React Context for authentication
- Local state for component data
- Axios interceptors for token refresh

## Technology Stack Compliance

### Backend (Strict Requirements)
✅ **Python + Django + Django REST Framework**
✅ **PostgreSQL** (configured, no SQLite/MongoDB)
✅ **LangChain** for ALL reasoning logic
✅ **Hugging Face Sentence Embeddings** ONLY for PDF processing
✅ **JWT Authentication** (no Django admin)

### Frontend (Strict Requirements)
✅ **React** with functional components and hooks
✅ **Axios** for API calls
✅ **Chart.js** for visualizations

### AI Implementation (Strict Requirements)
✅ **LangChain** handles:
- Expense categorization
- Savings advice generation
- Investment recommendations
- Chatbot responses
- Report summaries

✅ **Hugging Face** handles ONLY:
- PDF text semantic understanding
- Expense category prediction from PDF content

## User Role Handling

### Student Role Special Handling
- Monthly income is optional/hidden
- Can add pocket money optionally
- AI responses tailored for student context
- No fixed income assumptions in AI logic

### Other Roles (Professional, Freelancer, Teacher)
- Monthly income required for full features
- Role-specific AI recommendations
- Income-based budget analysis

## Features Implementation

### Core Features ✅
1. **User Authentication**: JWT-based, role selection
2. **Dashboard**: Income input, expense overview, AI suggestions
3. **Expense Management**: Manual entry + PDF upload with AI categorization
4. **AI Chatbot**: Personalized financial advice
5. **Savings Suggestions**: LangChain-generated, role-based
6. **Investment Ideas**: Educational, risk-appropriate
7. **Report Generation**: Date-range reports with AI summaries
8. **Visual Analytics**: Category breakdowns, spending trends

### AI Integration ✅
- **LangChain**: All reasoning and advice generation
- **Hugging Face**: PDF semantic understanding only
- **Personalization**: Based on user role and spending patterns
- **Context-Aware**: Uses user's financial data for responses

## Security & Best Practices

### Backend Security
- JWT token authentication
- CORS configuration
- Environment variables for secrets
- Input validation and sanitization
- PostgreSQL with proper user permissions

### Frontend Security
- Token storage in localStorage
- Automatic token refresh
- Protected routes
- Input validation
- HTTPS-ready configuration

## Deployment Ready

### Environment Configuration
- Separate development/production settings
- Environment variables for all secrets
- Database connection pooling ready
- Static file serving configured

### Scalability Considerations
- Stateless API design
- Database indexing on common queries
- Efficient AI model loading
- Component-based frontend architecture