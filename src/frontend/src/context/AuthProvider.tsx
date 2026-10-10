import { useState, ReactNode, useEffect, useCallback } from 'react';
import { AuthContext } from './AuthContext';
import { User } from './types';
import { setUnauthorizedHandler } from '../services/api';

const readSession = () => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  if (token && userStr) {
    try {
      const parsedUser = JSON.parse(userStr);
      if (typeof parsedUser === 'object' && parsedUser !== null && typeof parsedUser.name === 'string' && typeof parsedUser.email === 'string') {
        return { user: parsedUser as User, token };
      }
    } catch {
      // ignore
    }
  }
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  return { user: null, token: null };
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<{user: User | null, token: string | null}>(() => readSession());
  
  const isAuthenticated = session.user !== null && session.token !== null;

  const login = useCallback((token: string, userData: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setSession({ user: userData, token });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setSession({ user: null, token: null });
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    return () => {
      setUnauthorizedHandler(null);
    };
  }, [logout]);

  return (
    <AuthContext.Provider value={{ isAuthenticated, user: session.user, token: session.token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}


