'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CheckCircle, 
  AlertTriangle, 
  Zap,
  ArrowRight,
  Eye,
  Wrench
} from 'lucide-react';

interface FormatDetectionResult {
  detected: boolean;
  format_config?: object;
  confidence: number;
  pattern_name: string;
  canonical_examples: string[];
}

interface FormatDetectionDisplayProps {
  result: FormatDetectionResult | null;
  loading: boolean;
  error: string | null;
  originalExamples: string[];
  onAcceptFormat: () => void;
  onManualConfiguration: () => void;
}

export function FormatDetectionDisplay({
  result,
  loading,
  error,
  originalExamples,
  onAcceptFormat,
  onManualConfiguration
}: FormatDetectionDisplayProps) {
  if (loading) {
    return (
      <Card className="border-dashed">
        <CardContent className="p-6">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
            <span className="text-sm text-muted-foreground">
              Analyzing location patterns...
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!result) {
    return null;
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBadgeVariant = (confidence: number) => {
    if (confidence >= 80) return 'default';
    if (confidence >= 60) return 'secondary';
    return 'destructive';
  };

  const renderDetectionSuccess = () => (
    <Card className="border-green-200 bg-green-50/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-700">
          <CheckCircle className="h-5 w-5" />
          Pattern detected: {result.pattern_name}
        </CardTitle>
        <CardDescription className="flex items-center gap-2">
          <span>Confidence:</span>
          <Badge 
            variant={getConfidenceBadgeVariant(result.confidence)}
            className="font-medium"
          >
            {result.confidence}%
          </Badge>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress 
          value={result.confidence} 
          className="w-full h-2"
        />
        
        {/* Before/After Examples */}
        <div className="space-y-3">
          <div className="text-sm font-medium text-green-700">
            Conversion Preview
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">
                Your Examples
              </div>
              <div className="bg-white rounded-lg p-3 border">
                {originalExamples.slice(0, 5).map((example, index) => (
                  <div key={index} className="font-mono text-sm py-1">
                    {example}
                  </div>
                ))}
                {originalExamples.length > 5 && (
                  <div className="text-xs text-muted-foreground">
                    +{originalExamples.length - 5} more...
                  </div>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">
                Standardized Format
              </div>
              <div className="bg-white rounded-lg p-3 border">
                {result.canonical_examples.slice(0, 5).map((example, index) => (
                  <div key={index} className="font-mono text-sm py-1 text-green-700">
                    {example}
                  </div>
                ))}
                {result.canonical_examples.length > 5 && (
                  <div className="text-xs text-muted-foreground">
                    +{result.canonical_examples.length - 5} more...
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {originalExamples.length > 0 && result.canonical_examples.length > 0 && (
            <div className="flex items-center justify-center py-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Eye className="h-4 w-4" />
                <ArrowRight className="h-4 w-4" />
                <Zap className="h-4 w-4" />
                <span>Automatically converted</span>
              </div>
            </div>
          )}
        </div>

        {/* Status Indicator */}
        <div className="flex items-center justify-center gap-2 pt-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-green-700 font-medium">
              {result.confidence >= 90 ? "Perfect match - automatically applied!" : "Looks perfect"}
            </span>
          </div>
        </div>
        
        {/* Conditional Accept Button - only show for medium confidence */}
        {result.confidence < 90 && (
          <div className="flex justify-center pt-3">
            <Button 
              onClick={onAcceptFormat}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Use this format
            </Button>
          </div>
        )}
        
        {result.confidence < 80 && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Confidence is below 80%. You might want to review the detected pattern 
              or provide more examples for better accuracy.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  const renderDetectionFailure = () => (
    <Card className="border-yellow-200 bg-yellow-50/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-yellow-700">
          <AlertTriangle className="h-5 w-5" />
          No pattern detected
        </CardTitle>
        <CardDescription>
          We couldn't automatically detect a consistent location format pattern
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Try providing more examples or check that your location codes follow a consistent pattern.
            Examples: "01A", "325B", "245D" (Position + Level format)
          </AlertDescription>
        </Alert>
        
        <Button 
          onClick={onManualConfiguration}
          className="w-full"
          variant="outline"
        >
          <Wrench className="h-4 w-4 mr-2" />
          Configure format manually
        </Button>
      </CardContent>
    </Card>
  );

  return result.detected ? renderDetectionSuccess() : renderDetectionFailure();
}