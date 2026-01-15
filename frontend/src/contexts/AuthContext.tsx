'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { StoredUser, getStoredUser, isAuthenticated as checkIsAuthenticated } from '@/lib/auth-helper';

interface AuthContextType {
  user: StoredUser | null;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<StoredUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAuthStatus = async () => {
      try {
        const currentUser = getStoredUser();
        const authenticated = checkIsAuthenticated();

        setUser(currentUser);
        setIsAuthenticated(authenticated);
      } catch (error) {
        console.error('Error fetching auth status:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    fetchAuthStatus();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};