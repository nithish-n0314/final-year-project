import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from './Navbar';
import IncomeInput from './IncomeInput';
import ExpenseForm from './ExpenseForm';
import ExpenseChart from './ExpenseChart';
import SuggestionCards from './SuggestionCards';
import ChatBot from './ChatBot';
import ReportGenerator from './ReportGenerator';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/');
      setDashboardData(response.data);
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExpenseAdded = () => {
    fetchDashboardData();
  };

  const handleIncomeUpdated = () => {
    fetchDashboardData();
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="loading">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="alert alert-error">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="container">
        <h2>Welcome back, {user.username}!</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Role: {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
        </p>

        {/* Income Input - Hidden for students unless they want to add pocket money */}
        {user.role !== 'student' && (
          <IncomeInput 
            user={dashboardData.user} 
            onIncomeUpdated={handleIncomeUpdated}
          />
        )}
        
        {user.role === 'student' && !dashboardData.user.monthly_income && (
          <div className="card">
            <h3>Optional: Add Pocket Money</h3>
            <p style={{ marginBottom: '15px', color: '#666' }}>
              As a student, you can optionally track your pocket money or part-time income.
            </p>
            <IncomeInput 
              user={dashboardData.user} 
              onIncomeUpdated={handleIncomeUpdated}
              isOptional={true}
            />
          </div>
        )}

        <div className="grid grid-2">
          {/* Expense Management */}
          <div>
            <ExpenseForm onExpenseAdded={handleExpenseAdded} />
          </div>

          {/* Expense Visualization */}
          <div>
            <ExpenseChart insights={dashboardData.insights} />
          </div>
        </div>

        <div className="grid grid-2">
          {/* AI Suggestions */}
          <div>
            <SuggestionCards 
              savingsSuggestions={dashboardData.savings_suggestions}
              investmentIdeas={dashboardData.investment_ideas}
            />
          </div>

          {/* AI Chatbot */}
          <div>
            <ChatBot />
          </div>
        </div>

        {/* Report Generation */}
        <ReportGenerator />
      </div>
    </div>
  );
};

export default Dashboard;