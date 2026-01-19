# Coinsy

A complete full-stack web application for personalized financial management with AI-powered insights.

## 🚀 Features

- **User Authentication**: JWT-based authentication with role selection
- **Role-Based Personalization**: Student, Freelancer, Teacher, Professional
- **Expense Management**: Manual entry and PDF upload with AI categorization
- **AI-Powered Insights**: Savings suggestions and investment recommendations
- **Interactive Chatbot**: Personalized financial advice
- **Visual Analytics**: Category breakdowns and spending trends
- **Comprehensive Reports**: Date-range reports with AI summaries
- **PDF Processing**: Extract expenses from receipts and statements

## 🛠 Tech Stack

**Frontend:**
- React (functional components, hooks)
- Axios for API calls
- Chart.js for visualizations

**Backend:**
- Python + Django + Django REST Framework
- PostgreSQL database
- JWT authentication

**AI:**
- LangChain for reasoning logic
- Hugging Face Sentence Embeddings for PDF processing

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API key

## 🔧 Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**
```bash
python setup.py
```

2. **Set up PostgreSQL database:**
```sql
-- Connect as postgres superuser
psql -U postgres

-- Create database and user
CREATE DATABASE finance_assistant;
CREATE USER finance_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE finance_assistant TO finance_user;
\q
```

3. **Update environment variables:**
Edit `backend/.env` with your actual values:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=finance_assistant
DB_USER=finance_user
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key-here
```

4. **Run migrations:**
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

5. **Start the application:**

**Windows:**
```bash
# Terminal 1 - Backend
start-backend.bat

# Terminal 2 - Frontend
start-frontend.bat
```

**Linux/Mac:**
```bash
# Terminal 1 - Backend
chmod +x start-backend.sh
./start-backend.sh

# Terminal 2 - Frontend
chmod +x start-frontend.sh
./start-frontend.sh
```

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

5. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Start the server:**
```bash
python manage.py runserver
```

#### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```

## 🎯 Application Flow

1. **Registration/Login**: Users select their role (student, freelancer, teacher, professional)
2. **Dashboard Access**: Immediate redirect to dashboard after authentication
3. **Income Setup**: 
   - Non-students: Required monthly income input
   - Students: Optional pocket money (can be skipped)
4. **Expense Management**: Add expenses manually or upload PDF receipts
5. **AI Insights**: Get personalized savings and investment suggestions
6. **Chat Assistant**: Ask questions about finances
7. **Reports**: Generate detailed financial reports with AI analysis

## 🤖 AI Features

### LangChain Integration
- **Expense Categorization**: Automatically categorize expenses
- **Savings Suggestions**: Personalized based on role and spending
- **Investment Ideas**: Educational, risk-appropriate recommendations
- **Chatbot**: Context-aware financial advice
- **Report Summaries**: Natural language analysis of spending patterns

### Hugging Face Integration
- **PDF Processing**: Extract and understand expense data from PDFs
- **Semantic Matching**: Categorize expenses from PDF content

## 👥 User Roles

### Student
- Optional income tracking (pocket money)
- Student-specific AI advice
- No fixed income assumptions

### Professional/Freelancer/Teacher
- Monthly income tracking required
- Role-specific financial recommendations
- Budget analysis and tracking

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### User Management
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update user profile

### Expenses
- `GET /api/expenses/` - Get user expenses
- `POST /api/expenses/` - Add expense
- `POST /api/expenses/upload-pdf/` - Upload PDF expenses

### Dashboard & Analytics
- `GET /api/dashboard/` - Dashboard data with AI insights
- `GET /api/analytics/` - Expense analytics

### AI Features
- `POST /api/chat/` - AI chatbot
- `GET /api/chat/history/` - Chat history

### Reports
- `POST /api/reports/` - Generate financial reports

## 🔒 Security Features

- JWT token authentication
- Automatic token refresh
- Protected API endpoints
- Input validation and sanitization
- CORS configuration
- Environment variable protection

## 🚀 Production Deployment

### Environment Variables
Set the following in production:
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DB_NAME=finance_assistant
DB_USER=finance_user
DB_PASSWORD=secure_password
DB_HOST=your_db_host
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key
```

### Database
- Use PostgreSQL in production
- Set up proper database backups
- Configure connection pooling

### Frontend
```bash
cd frontend
npm run build
# Serve build folder with nginx or similar
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in .env
   - Verify database and user exist

2. **OpenAI API Error**
   - Verify API key is correct
   - Check API quota and billing

3. **PDF Upload Issues**
   - Ensure file is valid PDF
   - Check file size limits
   - Verify sentence-transformers installation

4. **Frontend Build Issues**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Development Tips

- Use `DEBUG=True` for development
- Check Django logs for backend issues
- Use browser dev tools for frontend debugging
- Monitor API calls in Network tab

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a complete implementation following strict requirements. All specified features are implemented according to the original specifications.