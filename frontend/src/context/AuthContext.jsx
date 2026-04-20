import { createContext, useContext, useState } from 'react';
import { login as apiLogin } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const role = localStorage.getItem('role');
    return token ? { token, userId, role } : null;
  });

  async function login(username, password) {
    const data = await apiLogin(username, password);
    const state = {
      token: data.access_token,
      userId: data.user_id,
      role: data.role,
    };
    localStorage.setItem('token', state.token);
    localStorage.setItem('userId', state.userId);
    localStorage.setItem('role', state.role);
    setAuth(state);
    return state;
  }

  function logout() {
    localStorage.clear();
    setAuth(null);
  }

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
