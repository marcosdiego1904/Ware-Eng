'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, Wifi, Lock, Zap } from 'lucide-react';
import { api } from '@/lib/api';

interface SmartConfigAuthDebugProps {
  onAuthFixed?: () => void;
}

interface DiagnosticResult {
  test: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  details?: string;
}

export function SmartConfigAuthDebug({ onAuthFixed }: SmartConfigAuthDebugProps) {
  const [diagnostics, setDiagnostics] = useState<DiagnosticResult[]>([]);
  const [loading, setLoading] = useState(false);

  const runDiagnostics = async () => {
    setLoading(true);
    const results: DiagnosticResult[] = [];

    // Test 1: Check if user is authenticated
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    results.push({
      test: 'Authentication Token',
      status: token ? 'pass' : 'fail',
      message: token ? 'Token found in localStorage' : 'No authentication token found',
      details: token ? `Token length: ${token.length} characters` : 'User needs to log in'
    });

    // Test 2: Test debug endpoint (no auth required)
    try {
      const debugResponse = await fetch('/api/debug/test-format-detection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ examples: ['010A', '325B', '245D'] })
      });

      if (debugResponse.ok) {
        const debugResult = await debugResponse.json();
        const patternDetected = debugResult.detection_result?.detected_pattern?.pattern_type || 'None';
        results.push({
          test: 'Backend Format Detection',
          status: 'pass',
          message: `Smart Configuration working perfectly`,
          details: `Detected pattern: ${patternDetected} with high confidence`
        });
      } else {
        results.push({
          test: 'Backend Format Detection',
          status: 'fail',
          message: `Debug endpoint failed: ${debugResponse.status}`,
          details: await debugResponse.text()
        });
      }
    } catch (error) {
      results.push({
        test: 'Backend Connectivity',
        status: 'fail',
        message: 'Cannot connect to backend',
        details: `Error: ${error}`
      });
    }

    // Test 3: Test main API endpoint with current auth
    if (token) {
      try {
        const mainResponse = await api.post('/templates/detect-format', {
          examples: ['010A', '325B', '245D'],
          warehouse_context: { name: 'Test' }
        });

        results.push({
          test: 'Authenticated API Call',
          status: 'pass',
          message: 'Smart Configuration API working with authentication',
          details: `Format detection successful with auth`
        });

        // If we reach here, auth is working!
        if (onAuthFixed) {
          onAuthFixed();
        }
      } catch (error: any) {
        const status = error.response?.status;
        if (status === 401) {
          results.push({
            test: 'Authenticated API Call',
            status: 'fail',
            message: 'Authentication token is invalid or expired',
            details: 'User needs to log out and log back in'
          });
        } else {
          results.push({
            test: 'Authenticated API Call',
            status: 'warning',
            message: `API call failed with status ${status}`,
            details: error.response?.data?.error || error.message
          });
        }
      }
    }

    setDiagnostics(results);
    setLoading(false);
  };

  const fixAuth = () => {
    // Clear invalid token and redirect to login
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/auth';
    }
  };

  const getStatusIcon = (status: DiagnosticResult['status']) => {
    switch (status) {
      case 'pass': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'fail': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: DiagnosticResult['status']) => {
    switch (status) {
      case 'pass': return <Badge variant="secondary" className="bg-green-100 text-green-800">PASS</Badge>;
      case 'fail': return <Badge variant="destructive">FAIL</Badge>;
      case 'warning': return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">WARN</Badge>;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-blue-500" />
          Smart Configuration Diagnostics
        </CardTitle>
        <CardDescription>
          Debug authentication and connectivity issues with Smart Configuration format detection
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Button onClick={runDiagnostics} disabled={loading}>
            {loading ? 'Running Tests...' : 'Run Diagnostics'}
          </Button>
          {diagnostics.some(d => d.status === 'fail' && d.test.includes('Auth')) && (
            <Button variant="outline" onClick={fixAuth}>
              Fix Authentication
            </Button>
          )}
        </div>

        {diagnostics.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium">Diagnostic Results:</h4>
            {diagnostics.map((result, index) => (
              <div key={index} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(result.status)}
                    <span className="font-medium">{result.test}</span>
                  </div>
                  {getStatusBadge(result.status)}
                </div>
                <p className="text-sm text-gray-600 mb-1">{result.message}</p>
                {result.details && (
                  <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    {result.details}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {diagnostics.length > 0 && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Summary:</strong> {' '}
              {diagnostics.filter(d => d.status === 'pass').length} tests passed, {' '}
              {diagnostics.filter(d => d.status === 'fail').length} failed, {' '}
              {diagnostics.filter(d => d.status === 'warning').length} warnings
              {diagnostics.some(d => d.status === 'fail' && d.test.includes('Auth')) && (
                <span className="block mt-2 text-sm">
                  🔧 <strong>Quick Fix:</strong> Click "Fix Authentication" to log in again
                </span>
              )}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}