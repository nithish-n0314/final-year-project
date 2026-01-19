import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const IncomeInput = ({ user, onIncomeUpdated, isOptional = false }) => {
  const [income, setIncome] = useState(user.monthly_income || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { updateUser } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.put('/profile/', {
        monthly_income: income || null
      });
      
      updateUser(response.data);
      setSuccess(isOptional ? 'Pocket money updated successfully!' : 'Monthly income updated successfully!');
      onIncomeUpdated();
    } catch (error) {
      setError('Failed to update income');
    } finally {
      setLoading(false);
    }
  };

  if (user.monthly_income && !isOptional) {
    return (
      <div className="card">
        <h3>Monthly Income</h3>
        <p style={{ fontSize: '24px', color: '#28a745', marginBottom: '10px' }}>
          ₹{parseFloat(user.monthly_income).toFixed(2)}
        </p>
        <button 
          onClick={() => setIncome(user.monthly_income)}
          className="btn btn-secondary"
          style={{ fontSize: '12px', padding: '5px 10px' }}
        >
          Update Income
        </button>
        
        {income && (
          <form onSubmit={handleSubmit} style={{ marginTop: '15px' }}>
            <div className="form-group">
              <label htmlFor="income">New Monthly Income</label>
              <input
                type="number"
                id="income"
                className="form-control"
                value={income}
                onChange={(e) => setIncome(e.target.value)}
                min="0"
                step="0.01"
                placeholder="Enter your monthly income"
              />
            </div>
            
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update'}
              </button>
              <button
                type="button"
                onClick={() => setIncome('')}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    );
  }

  return (
    <div className="card">
      <h3>{isOptional ? 'Add Pocket Money (Optional)' : 'Set Monthly Income'}</h3>
      <p style={{ marginBottom: '15px', color: '#666' }}>
        {isOptional 
          ? 'Track your pocket money or part-time income to get better financial insights.'
          : 'Please enter your monthly income to get personalized financial advice.'
        }
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="income">
            {isOptional ? 'Monthly Pocket Money/Income' : 'Monthly Income'}
          </label>
          <input
            type="number"
            id="income"
            className="form-control"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            min="0"
            step="0.01"
            placeholder={isOptional ? "Enter amount (optional)" : "Enter your monthly income"}
            required={!isOptional}
          />
        </div>
        
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Saving...' : (isOptional ? 'Save' : 'Set Income')}
          </button>
          
          {isOptional && (
            <button
              type="button"
              onClick={() => onIncomeUpdated()}
              className="btn btn-secondary"
            >
              Skip
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default IncomeInput;