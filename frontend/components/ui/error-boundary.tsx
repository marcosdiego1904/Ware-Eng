"use client"

import React from 'react'
import { AlertTriangle, RefreshCw, Home, ChevronLeft } from 'lucide-react'
import { Button } from './button'
import { Card, CardContent, CardHeader, CardTitle } from './card'

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<ErrorFallbackProps>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface ErrorFallbackProps {
  error: Error
  resetError: () => void
  goHome: () => void
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo
    })

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }

    // Call onError callback if provided
    this.props.onError?.(error, errorInfo)
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  goHome = () => {
    this.resetError()
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      
      return (
        <FallbackComponent
          error={this.state.error}
          resetError={this.resetError}
          goHome={this.goHome}
        />
      )
    }

    return this.props.children
  }
}

function DefaultErrorFallback({ error, resetError, goHome }: ErrorFallbackProps) {
  const isChunkError = error.message.includes('Loading chunk') || 
                      error.message.includes('ChunkLoadError')
  
  const isDevelopment = process.env.NODE_ENV === 'development'

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <CardTitle className="text-xl text-gray-900">
            {isChunkError ? 'Update Available' : 'Something went wrong'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600 text-center">
            {isChunkError 
              ? "A new version of the application is available. Please refresh the page to get the latest updates."
              : "We encountered an unexpected error. This has been logged and we're working to fix it."
            }
          </p>

          {isDevelopment && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                Technical Details (Development Only)
              </summary>
              <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono text-gray-800 overflow-auto max-h-32">
                {error.message}
                {error.stack && (
                  <pre className="mt-2 whitespace-pre-wrap">{error.stack}</pre>
                )}
              </div>
            </details>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              onClick={resetError}
              className="flex-1 flex items-center gap-2"
              variant="outline"
            >
              <RefreshCw className="w-4 h-4" />
              {isChunkError ? 'Refresh Page' : 'Try Again'}
            </Button>
            <Button
              onClick={goHome}
              className="flex-1 flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Go Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Simplified error boundary for smaller components
export function SimpleErrorBoundary({ 
  children, 
  message = "Something went wrong with this component"
}: { 
  children: React.ReactNode
  message?: string 
}) {
  return (
    <ErrorBoundary
      fallback={({ resetError }) => (
        <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
          <div className="flex items-center gap-2 text-red-800 mb-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">Error</span>
          </div>
          <p className="text-sm text-red-700 mb-3">{message}</p>
          <Button 
            size="sm" 
            variant="outline"
            onClick={resetError}
            className="text-red-700 border-red-300 hover:bg-red-100"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Retry
          </Button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  )
}

// Hook for imperative error handling
export function useErrorHandler() {
  return (error: Error, errorInfo?: { componentStack?: string }) => {
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Caught error:', error, errorInfo)
    }

    // In production, you might want to send to error tracking service
    // Example: Sentry.captureException(error, { extra: errorInfo })
  }
}