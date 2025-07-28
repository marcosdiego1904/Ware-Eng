"use client"

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ClearAuth() {
  const clearAuthData = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      console.log('Auth data cleared')
      
      // Show confirmation
      alert('Auth data cleared! Please refresh the page and login again.')
    }
  }

  const showCurrentAuth = () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      const user = localStorage.getItem('user')
      
      console.log('Current auth data:')
      console.log('Token:', token)
      console.log('User:', user)
      
      alert(`Token: ${token ? 'Present' : 'None'}\nUser: ${user || 'None'}`)
    }
  }

  const testBackendConnection = async () => {
    try {
      console.log('Testing backend connection...')
      
      // Test basic connection
      const response = await fetch('http://localhost:5001/api/v1/debug/config', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Backend connection successful:', data)
        alert(`Backend is running!\nCORS Origins: ${data.allowed_origins?.join(', ')}\nHas Secret Key: ${data.has_secret_key}`)
      } else {
        console.log('Backend responded with error:', response.status)
        alert(`Backend error: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Backend connection failed:', error)
      alert(`Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  return (
    <Card className="w-full max-w-md mt-4">
      <CardHeader>
        <CardTitle>Auth Token Management</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button onClick={testBackendConnection} variant="default" className="w-full">
          Test Backend Connection
        </Button>
        <Button onClick={showCurrentAuth} variant="outline" className="w-full">
          Show Current Auth Data
        </Button>
        <Button onClick={clearAuthData} variant="destructive" className="w-full">
          Clear Auth Data
        </Button>
        <p className="text-sm text-gray-600 mt-2">
          Use this if you're getting "Signature verification failed" errors
        </p>
      </CardContent>
    </Card>
  )
}