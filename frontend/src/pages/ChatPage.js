import React from 'react';
import Navbar from '../components/Navbar';
import ChatBot from '../components/ChatBot';

const ChatPage = () => {
  return (
    <div>
      <Navbar />
      <div className="container">
        <h2>AI Assistant</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Chat with your personal finance AI assistant
        </p>

        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <ChatBot />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;