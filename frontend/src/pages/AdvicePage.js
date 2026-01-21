import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import SuggestionCards from '../components/SuggestionCards';

const AdvicePage = () => {
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
      setError('Failed to load advice data');
      console.error('Advice error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="loading">Loading AI advice...</div>
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
        <h2>AI Financial Advice</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Personalized savings and investment recommendations based on your profile
        </p>

        <SuggestionCards 
          savingsSuggestions={dashboardData.savings_suggestions}
          investmentIdeas={dashboardData.investment_ideas}
        />
      </div>
    </div>
  );
};

export default AdvicePage;