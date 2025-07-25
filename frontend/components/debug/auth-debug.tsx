"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function AuthDebug() {
  const { login, register, user, isAuth, isLoading } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogin = async () => {
    try {
      setError('')
      setSuccess('')
      await login(username, password)
      setSuccess('Login successful!')
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.response?.data?.message || err.message || 'Login failed')
    }
  }

  const handleRegister = async () => {
    try {
      setError('')
      setSuccess('')
      await register(username, password)
      setSuccess('Registration successful!')
    } catch (err: any) {
      console.error('Register error:', err)
      setError(err.response?.data?.message || err.message || 'Registration failed')
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
        </CardContent>
      </Card>
    </div>
  )
}