import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';

const ChatBot = () => {
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      content: 'Hi! I\'m Coinsy. Ask me anything about your spending, savings, or investments!',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to chat
    setMessages(prev => [...prev, {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);

    setLoading(true);

    try {
      const response = await api.post('/chat/', {
        message: userMessage
      });

      // Add AI response to chat
      setMessages(prev => [...prev, {
        type: 'ai',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp)
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    "How can I save more money?",
    "Where should I invest?",
    "Summarize my spending",
    "Am I overspending this month?"
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  return (
    <div className="card">
      <h3>AI Finance Assistant</h3>
      
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.type}`}>
              <div className={`chat-bubble ${message.type}`}>
                {message.content}
              </div>
              <div style={{ 
                fontSize: '11px', 
                color: '#666', 
                marginTop: '4px',
                textAlign: message.type === 'user' ? 'right' : 'left'
              }}>
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="chat-message ai">
              <div className="chat-bubble ai">
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span>Thinking</span>
                  <div style={{ display: 'flex', gap: '2px' }}>
                    <div style={{ 
                      width: '4px', 
                      height: '4px', 
                      backgroundColor: '#666', 
                      borderRadius: '50%',
                      animation: 'pulse 1.5s infinite'
                    }}></div>
                    <div style={{ 
                      width: '4px', 
                      height: '4px', 
                      backgroundColor: '#666', 
                      borderRadius: '50%',
                      animation: 'pulse 1.5s infinite 0.5s'
                    }}></div>
                    <div style={{ 
                      width: '4px', 
                      height: '4px', 
                      backgroundColor: '#666', 
                      borderRadius: '50%',
                      animation: 'pulse 1.5s infinite 1s'
                    }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
            Quick questions:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                style={{
                  padding: '4px 8px',
                  fontSize: '11px',
                  border: '1px solid #ddd',
                  borderRadius: '12px',
                  background: 'white',
                  cursor: 'pointer',
                  color: '#007bff'
                }}
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="chat-input">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me about your finances..."
            disabled={loading}
            className="form-control"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !inputMessage.trim()}
          >
            Send
          </button>
        </form>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 80%, 100% {
            opacity: 0.3;
          }
          40% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatBot;