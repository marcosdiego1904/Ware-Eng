"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { User, authApi, setAuthToken, getAuthToken, removeAuthToken, setUser, getUser } from './auth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string, invitationCode: string) => Promise<void>
  logout: () => void
  isAuth: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuth, setIsAuth] = useState(false)

  useEffect(() => {
    const initAuth = () => {
      const token = getAuthToken()
      const userData = getUser()
      
      if (token && userData) {
        setUserState(userData)
        setIsAuth(true)
      } else {
        setUserState(null)
        setIsAuth(false)
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password })
      const userData = { username: response.username }
      
      setAuthToken(response.token)
      setUser(userData)
      setUserState(userData)
      setIsAuth(true)
    } catch (error) {
      throw error
    }
  }

  const register = async (username: string, password: string, invitationCode: string) => {
    try {
      await authApi.register({ username, password, invitation_code: invitationCode })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    removeAuthToken()
    setUserState(null)
    setIsAuth(false)
    
    // Clear all user-specific Zustand stores to prevent data contamination
    if (typeof window !== 'undefined') {
      // Clear location store
      try {
        const { default: useLocationStore } = require('./location-store');
        useLocationStore.getState().resetStore();
        console.log('🔄 Location store reset on logout');
      } catch (error) {
        console.warn('Failed to reset location store:', error);
      }
      
      // Clear other stores if needed
      try {
        const { useRulesStore } = require('./rules-store');
        if (useRulesStore?.getState()?.resetStore) {
          useRulesStore.getState().resetStore();
          console.log('🔄 Rules store reset on logout');
        }
      } catch (error) {
        console.warn('Failed to reset rules store:', error);
      }
    }
    
    // Force page reload to ensure completely clean state
    if (typeof window !== 'undefined') {
      window.location.href = '/auth'
    }
  }

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuth
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}