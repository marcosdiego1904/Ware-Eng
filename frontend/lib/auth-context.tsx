"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { User, authApi, setAuthToken, getAuthToken, removeAuthToken, setUser, getUser } from './auth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
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

  const register = async (username: string, password: string) => {
    try {
      await authApi.register({ username, password })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    removeAuthToken()
    setUserState(null)
    setIsAuth(false)
    // Force page reload to ensure clean state
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