import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import ExpenseForm from '../components/ExpenseForm';
import ExpenseChart from '../components/ExpenseChart';

const ExpensesPage = () => {
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
      setError('Failed to load expense data');
      console.error('Expenses error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExpenseAdded = () => {
    fetchDashboardData();
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="loading">Loading expenses...</div>
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
        <h2>Expense Management</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Track your expenses manually or upload PDF receipts
        </p>

        <div className="grid grid-2">
          {/* Expense Form */}
          <div>
            <ExpenseForm onExpenseAdded={handleExpenseAdded} />
          </div>

          {/* Expense Visualization */}
          <div>
            <ExpenseChart insights={dashboardData.insights} />
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>Recent Transactions</h3>
          {dashboardData.insights.recent_transactions.length > 0 ? (
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {dashboardData.insights.recent_transactions.map((transaction, index) => (
                <div key={index} className="expense-item">
                  <div>
                    <div style={{ fontWeight: '500' }}>{transaction.description}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {transaction.category} • {transaction.date}
                    </div>
                  </div>
                  <div style={{ fontWeight: 'bold', color: '#dc3545' }}>
                    -₹{transaction.amount.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
              No transactions yet. Add your first expense above!
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExpensesPage;