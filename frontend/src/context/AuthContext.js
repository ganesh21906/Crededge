import React, { createContext, useContext, useState, useCallback } from 'react';
import { adminLogin } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [adminToken, setAdminToken] = useState(() =>
    localStorage.getItem('crededge_admin_token')
  );
  const [adminUser, setAdminUser] = useState(() =>
    localStorage.getItem('crededge_admin_user')
  );
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  const login = useCallback(async (username, password) => {
    setLoginLoading(true);
    setLoginError('');
    try {
      const data = await adminLogin(username, password);
      localStorage.setItem('crededge_admin_token', data.access_token);
      localStorage.setItem('crededge_admin_user', data.username);
      setAdminToken(data.access_token);
      setAdminUser(data.username);
      return true;
    } catch (err) {
      let detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        detail = detail.map(e => `${e.loc?.slice(-1)}: ${e.msg}`).join(', ');
      } else if (typeof detail === 'object') {
        detail = JSON.stringify(detail);
      }
      setLoginError(detail || 'Invalid credentials. Please try again.');
      return false;
    } finally {
      setLoginLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('crededge_admin_token');
    localStorage.removeItem('crededge_admin_user');
    setAdminToken(null);
    setAdminUser(null);
  }, []);

  const isAuthenticated = Boolean(adminToken);

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      adminUser,
      login,
      logout,
      loginError,
      loginLoading,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
