import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
  };

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h1>Coinsy</h1>
        </Link>
        
        <div className="nav-links">
          <Link to="/dashboard" className={isActive('/dashboard')}>
            📊 Dashboard
          </Link>
          <Link to="/expenses" className={isActive('/expenses')}>
            💰 Expenses
          </Link>
          <Link to="/advice" className={isActive('/advice')}>
            💡 Advice
          </Link>
          <Link to="/chat" className={isActive('/chat')}>
            🤖 AI Chat
          </Link>
          <Link to="/reports" className={isActive('/reports')}>
            📄 Reports
          </Link>
        </div>

        <div className="user-info">
          <span>Hello, {user.username}</span>
          <button 
            onClick={handleLogout}
            className="btn btn-secondary"
            style={{ padding: '8px 16px' }}
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;