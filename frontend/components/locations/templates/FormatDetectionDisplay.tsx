'use client';

import React, { useState } from 'react';
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
  Wrench,
  Loader2
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
  isApplied?: boolean;
}

export function FormatDetectionDisplay({
  result,
  loading,
  error,
  originalExamples,
  onAcceptFormat,
  onManualConfiguration,
  isApplied = false
}: FormatDetectionDisplayProps) {
  const [isApplying, setIsApplying] = useState(false);
  
  const handleApplyFormat = () => {
    setIsApplying(true);
    // Call the callback immediately to update parent state
    onAcceptFormat();
    // Brief delay just for visual feedback
    setTimeout(() => {
      setIsApplying(false);
    }, 500);
  };

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

  const getConfidenceBadgeVariant = (confidence: number) => {
    if (confidence >= 80) return 'default';
    if (confidence >= 60) return 'secondary';
    return 'destructive';
  };

  const renderDetectionSuccess = () => (
    <Card className={`transition-all duration-300 ${
      isApplied 
        ? "border-green-200 bg-green-50/50" 
        : "border-blue-200 bg-blue-50/50"
    }`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className={`flex items-center gap-2 ${
            isApplied ? "text-green-700" : "text-blue-700"
          }`}>
            {isApplied ? (
              <>
                <CheckCircle className="h-5 w-5" />
                Format Configuration Applied
              </>
            ) : (
              <>
                <Zap className="h-5 w-5" />
                Pattern detected: {result.pattern_name}
              </>
            )}
          </CardTitle>
          <Badge 
            variant={getConfidenceBadgeVariant(result.confidence)}
            className="font-medium"
          >
            {result.confidence}%
          </Badge>
        </div>
        <CardDescription className={isApplied ? "text-green-600" : "text-blue-600"}>
          {isApplied 
            ? "Your template is now configured with this location format pattern."
            : "High-confidence format detection complete. Apply to configure your template."
          }
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Simplified Progress Indicator */}
        <Progress 
          value={result.confidence} 
          className="w-full h-2"
        />
        
        {/* Condensed Before/After Examples (max 3 items) */}
        {!isApplied && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">
                Your Examples
              </div>
              <div className="bg-white rounded-lg p-3 border">
                {originalExamples.slice(0, 3).map((example, index) => (
                  <div key={index} className="font-mono text-sm py-1">
                    {example}
                  </div>
                ))}
                {originalExamples.length > 3 && (
                  <div className="text-xs text-muted-foreground">
                    +{originalExamples.length - 3} more...
                  </div>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">
                Standardized Format
              </div>
              <div className="bg-white rounded-lg p-3 border">
                {result.canonical_examples.slice(0, 3).map((example, index) => (
                  <div key={index} className="font-mono text-sm py-1 text-green-700">
                    {example}
                  </div>
                ))}
                {result.canonical_examples.length > 3 && (
                  <div className="text-xs text-muted-foreground">
                    +{result.canonical_examples.length - 3} more...
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Clean Action Button with State Management */}
        <div className="flex justify-center pt-4">
          {isApplied ? (
            <div className="flex items-center gap-2 px-6 py-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-green-700 font-medium">
                Successfully Applied!
              </span>
            </div>
          ) : (
            <Button 
              onClick={handleApplyFormat}
              disabled={isApplying}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 text-base"
              size="lg"
            >
              {isApplying ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Applying...
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Apply Format Configuration →
                </>
              )}
            </Button>
          )}
        </div>
        
        {/* Low confidence warning - only show if not applied and confidence is low */}
        {!isApplied && result.confidence < 80 && (
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