'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, RefreshCw, Bug, Home } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallbackTitle?: string;
  fallbackDescription?: string;
  showDetails?: boolean;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      const { 
        fallbackTitle = "Something went wrong", 
        fallbackDescription = "An unexpected error occurred in the warehouse settings.",
        showDetails = process.env.NODE_ENV === 'development'
      } = this.props;

      return (
        <div className="p-6 space-y-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {fallbackDescription}
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bug className="h-5 w-5" />
                {fallbackTitle}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                We apologize for the inconvenience. The warehouse settings section encountered an error.
              </p>

              <div className="flex gap-2">
                <Button onClick={this.handleRetry} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                <Button onClick={this.handleReload} variant="outline">
                  <Home className="h-4 w-4 mr-2" />
                  Reload Page
                </Button>
              </div>

              {showDetails && this.state.error && (
                <div className="mt-6">
                  <details className="bg-muted p-4 rounded-md">
                    <summary className="cursor-pointer font-semibold mb-2">
                      Technical Details (Development Mode)
                    </summary>
                    <div className="space-y-2 text-sm">
                      <div>
                        <strong>Error:</strong>
                        <pre className="mt-1 text-xs bg-background p-2 rounded overflow-x-auto">
                          {this.state.error.message}
                        </pre>
                      </div>
                      
                      {this.state.error.stack && (
                        <div>
                          <strong>Stack Trace:</strong>
                          <pre className="mt-1 text-xs bg-background p-2 rounded overflow-x-auto whitespace-pre-wrap">
                            {this.state.error.stack}
                          </pre>
                        </div>
                      )}
                      
                      {this.state.errorInfo?.componentStack && (
                        <div>
                          <strong>Component Stack:</strong>
                          <pre className="mt-1 text-xs bg-background p-2 rounded overflow-x-auto whitespace-pre-wrap">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </div>
                      )}
                    </div>
                  </details>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);
  
  const handleError = React.useCallback((error: Error | string) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    setError(errorObj);
    console.error('Error handled by useErrorHandler:', errorObj);
  }, []);
  
  const clearError = React.useCallback(() => {
    setError(null);
  }, []);
  
  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);
  
  return { handleError, clearError };
}

// Specific error boundary for warehouse settings
export function WarehouseSettingsErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallbackTitle="Warehouse Settings Error"
      fallbackDescription="There was an error loading the warehouse settings. This could be due to a network issue or a problem with the warehouse configuration."
      onError={(error, errorInfo) => {
        // Log to analytics or error reporting service
        console.error('Warehouse Settings Error:', {
          error: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          timestamp: new Date().toISOString()
        });
      }}
    >
      {children}
    </ErrorBoundary>
  );
}