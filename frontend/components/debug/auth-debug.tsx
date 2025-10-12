"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ClearAuth } from './clear-auth'

interface ApiTestResult {
  status?: number;
  statusText?: string;
  success: boolean;
  data?: unknown;
  error?: string;
  timestamp: string;
}

export function AuthDebug() {
  const { login, register, user, isAuth, isLoading } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [mounted, setMounted] = useState(false)
  const [apiTestResult, setApiTestResult] = useState<ApiTestResult | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogin = async () => {
    try {
      setError('')
      setSuccess('')
      await login(username, password)
      setSuccess('Login successful!')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string }
      console.error('Login error:', err)
      setError(error.response?.data?.message || error.message || 'Login failed')
    }
  }

  const handleRegister = async () => {
    try {
      setError('')
      setSuccess('')
      // Use BOOTSTRAP2025 as default invitation code for debug testing
      await register(username, password, 'BOOTSTRAP2025')
      setSuccess('Registration successful!')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string }
      console.error('Register error:', err)
      setError(error.response?.data?.message || error.message || 'Registration failed')
    }
  }

  const testRulesAPI = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      console.log('Testing rules API with token:', token ? 'Present' : 'None')
      
      // Import the configured API instance
      const { api } = await import('@/lib/api')
      
      const response = await api.get('/rules')
      
      setApiTestResult({
        status: response.status,
        statusText: response.statusText,
        success: response.status < 400,
        data: response.data,
        timestamp: new Date().toISOString()
      })
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string }; status?: number }; message?: string }
      console.error('API test error:', err)
      setApiTestResult({
        success: false,
        error: error.response?.data?.message || error.message || 'Unknown error',
        status: error.response?.status,
        timestamp: new Date().toISOString()
      })
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Auth Debug</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p><strong>Is Loading:</strong> {isLoading ? 'Yes' : 'No'}</p>
            <p><strong>Is Authenticated:</strong> {isAuth ? 'Yes' : 'No'}</p>
            <p><strong>User:</strong> {user ? user.username : 'None'}</p>
            <p><strong>Token:</strong> {mounted ? (localStorage.getItem('auth_token') ? 'Present' : 'None') : 'Loading...'}</p>
          </div>

          <div className="space-y-2">
            <Input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="flex gap-2">
            <Button onClick={handleLogin} className="flex-1">
              Login
            </Button>
            <Button onClick={handleRegister} variant="outline" className="flex-1">
              Register
            </Button>
          </div>

          <Button onClick={testRulesAPI} className="w-full" variant="secondary">
            Test Rules API
          </Button>

          {error && (
            <div className="p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-2 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}

          {apiTestResult && (
            <div className="p-2 border rounded text-sm">
              <strong>Rules API Test Result:</strong>
              <pre className="mt-1 text-xs overflow-auto max-h-32">
                {JSON.stringify(apiTestResult, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
      
      <ClearAuth />
    </div>
  )
}