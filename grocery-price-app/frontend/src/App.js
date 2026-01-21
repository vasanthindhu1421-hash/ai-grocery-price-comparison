import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import ProductDetails from './pages/ProductDetails';
import Login from './pages/Login';
import Signup from './pages/Signup';
import { verifyAuth } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await verifyAuth();
      if (response.valid) {
        setIsAuthenticated(true);
        setUser(response.user);
        localStorage.setItem('user', JSON.stringify(response.user));
      } else {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    } catch (error) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  const ProtectedRoute = ({ children }) => {
    if (loading) {
      return <div className="loading-screen">Loading...</div>;
    }
    return isAuthenticated ? children : <Navigate to="/login" />;
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        {isAuthenticated && (
          <header className="app-header">
            <div className="header-content">
              <h1>🛒 Grocery Price Comparison</h1>
              <div className="header-actions">
                {user && <span className="user-name">Welcome, {user.username}</span>}
                <button onClick={handleLogout} className="logout-button">
                  Logout
                </button>
              </div>
            </div>
          </header>
        )}
        <main className="app-main">
          <Routes>
            <Route 
              path="/login" 
              element={
                isAuthenticated ? (
                  <Navigate to="/home" />
                ) : (
                  <Login onLoginSuccess={(user) => {
                    setIsAuthenticated(true);
                    setUser(user);
                  }} />
                )
              } 
            />
            <Route 
              path="/signup" 
              element={
                isAuthenticated ? (
                  <Navigate to="/home" />
                ) : (
                  <Signup onLoginSuccess={(user) => {
                    setIsAuthenticated(true);
                    setUser(user);
                  }} />
                )
              } 
            />
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route
              path="/"
              element={<Navigate to={isAuthenticated ? "/home" : "/signup"} />}
            />
            <Route
              path="/product/:id"
              element={
                <ProtectedRoute>
                  <ProductDetails />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
        {isAuthenticated && (
          <footer className="app-footer">
            <p>&copy; 2025 Grocery Price Comparison App - Compare prices across BigBasket, Zepto, Instamart, JioMart & Amazon Fresh</p>
          </footer>
        )}
      </div>
    </Router>
  );
}

export default App;

