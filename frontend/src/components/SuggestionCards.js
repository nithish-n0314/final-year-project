import React, { useState } from 'react';

const SuggestionCards = ({ savingsSuggestions, investmentIdeas }) => {
  const [activeTab, setActiveTab] = useState('savings');

  return (
    <div className="card">
      <h3>AI Recommendations</h3>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid #ddd' }}>
        <button
          onClick={() => setActiveTab('savings')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'savings' ? '#28a745' : 'transparent',
            color: activeTab === 'savings' ? 'white' : '#28a745',
            cursor: 'pointer',
            marginRight: '10px',
            borderRadius: '4px 4px 0 0'
          }}
        >
          Savings Tips
        </button>
        <button
          onClick={() => setActiveTab('investments')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'investments' ? '#007bff' : 'transparent',
            color: activeTab === 'investments' ? 'white' : '#007bff',
            cursor: 'pointer',
            borderRadius: '4px 4px 0 0'
          }}
        >
          Investment Ideas
        </button>
      </div>

      {activeTab === 'savings' && (
        <div>
          {savingsSuggestions && savingsSuggestions.length > 0 ? (
            savingsSuggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-card">
                <h4>{suggestion.title}</h4>
                <p style={{ marginBottom: '8px' }}>{suggestion.description}</p>
                <div className="savings">
                  Potential Savings: {suggestion.estimated_savings}
                </div>
                {suggestion.affordability_explanation && (
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#007bff', 
                    marginTop: '8px',
                    fontStyle: 'italic',
                    backgroundColor: '#f8f9fa',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}>
                    💡 {suggestion.affordability_explanation}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
              Add some expenses to get personalized savings suggestions!
            </p>
          )}
        </div>
      )}

      {activeTab === 'investments' && (
        <div>
          {investmentIdeas && investmentIdeas.length > 0 ? (
            investmentIdeas.map((idea, index) => (
              <div key={index} className="suggestion-card">
                <h4>{idea.title}</h4>
                <p style={{ marginBottom: '8px' }}>{idea.description}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#007bff' }}>
                    Risk: {idea.risk_level}
                  </span>
                  <span style={{ color: '#28a745' }}>
                    Min: {idea.min_investment}
                  </span>
                </div>
                {idea.affordability_explanation && (
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#007bff', 
                    marginTop: '8px',
                    fontStyle: 'italic',
                    backgroundColor: '#f8f9fa',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}>
                    💰 {idea.affordability_explanation}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
              Set up your profile to get personalized investment ideas!
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default SuggestionCards;