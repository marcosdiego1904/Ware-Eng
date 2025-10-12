"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { authApi } from '@/lib/auth'
import axios from 'axios'
import api from '@/lib/api'

export function ApiTest() {
  const [result, setResult] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const testConnection = async () => {
    setIsLoading(true)
    setResult('Testing connection...')
    
    try {
      // Test basic connection to Flask backend (without auth)
      await axios.get('http://localhost:5001/', {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 5000
      })
      setResult(`✅ Backend is reachable! Testing auth endpoints...`)
      
      // Now test a simple auth endpoint
      try {
        await axios.post('http://localhost:5001/api/v1/auth/login', {
          username: 'nonexistent',
          password: 'test'
        })
      } catch (authError: unknown) {
        const error = authError as { response?: { status?: number }; message?: string }
        if (error.response?.status === 401) {
          setResult(`✅ Connection successful! Auth endpoint responding correctly (401 for invalid creds)`)
        } else {
          setResult(`⚠️ Backend connected but auth endpoint error: ${error.message}`)
        }
      }
    } catch (error: unknown) {
      const err = error as { message?: string; code?: string }
      console.error('Connection test failed:', error)
      setResult(`❌ Connection failed: ${err.message}
        
Details: ${err.code || 'Unknown error'}
Is your Flask backend running on http://localhost:5001?`)
    } finally {
      setIsLoading(false)
    }
  }

  const testRegister = async () => {
    setIsLoading(true)
    setResult('Testing registration...')
    
    try {
      const testUsername = `test_${Date.now()}`
      await authApi.register({ username: testUsername, password: 'test123', invitation_code: 'BOOTSTRAP2025' })
      setResult(`✅ Registration successful for user: ${testUsername}`)
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { status?: number; data?: unknown } }
      console.error('Registration test failed:', error)
      setResult(`❌ Registration failed: ${err.message}
        
Status: ${err.response?.status}
Data: ${JSON.stringify(err.response?.data)}`)
    } finally {
      setIsLoading(false)
    }
  }

  const testLogin = async () => {
    setIsLoading(true)
    setResult('Testing login...')
    
    try {
      // Try to login with a test user (you might need to create one first)
      const response = await authApi.login({ username: 'testuser', password: 'test123' })
      setResult(`✅ Login successful! Token: ${response.token.substring(0, 20)}...`)
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { status?: number; data?: unknown } }
      console.error('Login test failed:', error)
      setResult(`❌ Login failed: ${err.message}
        
Status: ${err.response?.status}
Data: ${JSON.stringify(err.response?.data)}
        
💡 Try clicking "Test Register" first to create a test user!`)
    } finally {
      setIsLoading(false)
    }
  }

  const testFullFlow = async () => {
    setIsLoading(true)
    setResult('Testing full registration + login flow...')
    
    try {
      const testUsername = `test_${Date.now()}`
      const testPassword = 'test123'
      
      // Step 1: Register
      setResult(`Step 1: Registering user ${testUsername}...`)
      await authApi.register({ username: testUsername, password: testPassword, invitation_code: 'BOOTSTRAP2025' })
      
      // Step 2: Login
      setResult(`Step 2: Logging in with ${testUsername}...`)
      const response = await authApi.login({ username: testUsername, password: testPassword })
      
      setResult(`✅ Full flow successful! 
        
User: ${testUsername}
Token: ${response.token.substring(0, 30)}...
        
🎉 Authentication is working correctly!`)
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { status?: number; data?: unknown } }
      console.error('Full flow test failed:', error)
      setResult(`❌ Full flow failed: ${err.message}
        
Status: ${err.response?.status}
Data: ${JSON.stringify(err.response?.data)}`)
    } finally {
      setIsLoading(false)
    }
  }

  const testCors = async () => {
    setIsLoading(true)
    setResult('Testing CORS with same API instance used for auth...')
    
    try {
      // Use the same api instance that works for authentication
      const response = await api.post('/test', { test: 'data' })
      setResult(`✅ CORS test successful! 
        
Response: ${JSON.stringify(response.data)}
Status: ${response.status}

🎉 CORS is working correctly!`)
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { status?: number; data?: unknown }; code?: string; config?: { url?: string } }
      console.error('CORS test failed:', error)
      setResult(`❌ CORS test failed: ${err.message}
        
Status: ${err.response?.status}
Data: ${JSON.stringify(err.response?.data)}
Error Code: ${err.code}
URL: ${err.config?.url}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>API Connection Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2 flex-wrap">
          <Button onClick={testConnection} disabled={isLoading}>
            Test Connection
          </Button>
          <Button onClick={testRegister} disabled={isLoading}>
            Test Register
          </Button>
          <Button onClick={testLogin} disabled={isLoading}>
            Test Login
          </Button>
          <Button onClick={testFullFlow} disabled={isLoading} variant="default">
            🚀 Test Full Flow
          </Button>
          <Button onClick={testCors} disabled={isLoading} variant="outline">
            🌐 Test CORS
          </Button>
        </div>
        
        {result && (
          <div className="p-4 bg-gray-100 rounded-lg">
            <pre className="text-sm whitespace-pre-wrap">{result}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}