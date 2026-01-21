import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import IncomeInput from '../components/IncomeInput';

const DashboardPage = () => {
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

  const handleIncomeUpdated = () => {
    // Refresh dashboard data when income is updated
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
        <h2>Dashboard</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Welcome back, {user.username}! ({user.role.charAt(0).toUpperCase() + user.role.slice(1)})
        </p>

        {/* Income Input - Always visible */}
        <IncomeInput 
          user={user} 
          onIncomeUpdated={handleIncomeUpdated}
          isOptional={false}
        />

        {/* Quick Stats */}
        <div className="grid grid-3" style={{ marginTop: '20px' }}>
          <div className="stats-card">
            <h4>Total Expenses</h4>
            <div className="value">
              ₹{dashboardData.insights.total_this_month.toFixed(2)}
            </div>
            <div className="label">This Month</div>
          </div>
          
          <div className="stats-card">
            <h4>Transactions</h4>
            <div className="value">
              {dashboardData.insights.recent_transactions.length}
            </div>
            <div className="label">Recent</div>
          </div>
          
          <div className="stats-card">
            <h4>Categories</h4>
            <div className="value">
              {dashboardData.insights.categories.length}
            </div>
            <div className="label">Active</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;