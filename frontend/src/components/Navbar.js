import React from 'react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <nav className="navbar">
      <div className="container">
        <h1>Coinsy</h1>
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