import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

const ExpenseChart = ({ insights }) => {
  if (!insights || !insights.categories || insights.categories.length === 0) {
    return (
      <div className="card">
        <h3>Expense Overview</h3>
        <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
          No expenses recorded yet. Add some expenses to see your spending breakdown.
        </p>
      </div>
    );
  }

  // Prepare data for pie chart
  const pieData = {
    labels: insights.categories.map(cat => 
      cat.category.charAt(0).toUpperCase() + cat.category.slice(1)
    ),
    datasets: [
      {
        data: insights.categories.map(cat => cat.amount),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384',
          '#C9CBCF',
          '#4BC0C0',
          '#FF6384'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const percentage = context.parsed.toFixed(1);
            const amount = insights.categories[context.dataIndex].amount;
            return `${context.label}: ₹${amount.toFixed(2)} (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <div className="card">
      <h3>Expense Overview</h3>
      
      {/* Summary Stats */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span>Total This Month:</span>
          <strong>₹{insights.total_this_month.toFixed(2)}</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span>Transactions:</span>
          <strong>{insights.transaction_count}</strong>
        </div>
        
        {insights.budget_analysis && (
          <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Monthly Income:</span>
              <strong>₹{insights.budget_analysis.monthly_income.toFixed(2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Remaining Budget:</span>
              <strong style={{ 
                color: insights.budget_analysis.is_over_budget ? '#dc3545' : '#28a745' 
              }}>
                ₹{insights.budget_analysis.remaining_budget.toFixed(2)}
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Budget Used:</span>
              <strong style={{ 
                color: insights.budget_analysis.budget_percentage > 80 ? '#dc3545' : '#007bff' 
              }}>
                {insights.budget_analysis.budget_percentage.toFixed(1)}%
              </strong>
            </div>
          </div>
        )}
      </div>

      {/* Pie Chart */}
      <div style={{ maxWidth: '400px', margin: '0 auto' }}>
        <Pie data={pieData} options={pieOptions} />
      </div>

      {/* Recent Transactions */}
      {insights.recent_transactions && insights.recent_transactions.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h4>Recent Transactions</h4>
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {insights.recent_transactions.map((transaction, index) => (
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
        </div>
      )}
    </div>
  );
};

export default ExpenseChart;