"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { LoginForm } from '@/components/auth/login-form'
import { RegisterForm } from '@/components/auth/register-form'
import { useAuth } from '@/lib/auth-context'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2 } from 'lucide-react'

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [showSuccess, setShowSuccess] = useState(false)
  const { isAuth, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuth) {
      router.push('/')
    }
  }, [isAuth, isLoading, router])

  const handleRegisterSuccess = () => {
    setShowSuccess(true)
    setIsLogin(true)
    setTimeout(() => setShowSuccess(false), 5000)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-4">
        {showSuccess && (
          <Alert className="border-green-500 bg-green-50 text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              Account created successfully! You can now sign in.
            </AlertDescription>
          </Alert>
        )}
        
        {isLogin ? (
          <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <RegisterForm 
            onSwitchToLogin={() => setIsLogin(true)}
            onSuccess={handleRegisterSuccess}
          />
        )}
      </div>
    </div>
  )
}