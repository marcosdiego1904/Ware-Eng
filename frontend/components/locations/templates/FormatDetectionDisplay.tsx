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
    <Card className={`transition-all duration-300 shadow-lg ${
      isApplied 
        ? "border-emerald-200 bg-gradient-to-br from-emerald-50 to-slate-50" 
        : "border-slate-200 bg-gradient-to-br from-slate-50 to-blue-50"
    }`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className={`flex items-center gap-2 ${
            isApplied ? "text-emerald-700" : "text-slate-700"
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
        <CardDescription className={isApplied ? "text-emerald-600" : "text-slate-600"}>
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
            <div className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-50 to-slate-50 border border-emerald-200 rounded-lg shadow-sm">
              <CheckCircle className="h-5 w-5 text-emerald-600" />
              <span className="text-emerald-700 font-medium">
                Successfully Applied!
              </span>
            </div>
          ) : (
            <Button 
              onClick={handleApplyFormat}
              disabled={isApplying}
              className="bg-gradient-to-r from-slate-700 to-blue-700 hover:from-slate-800 hover:to-blue-800 text-white font-semibold px-8 py-4 text-base shadow-lg"
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
          We couldn't automatically detect a consistent location format pattern from your examples
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Enhanced troubleshooting with specific pattern examples */}
        <div className="bg-white rounded-lg border p-4 space-y-3">
          <div className="font-medium text-slate-700">Common patterns we recognize:</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="space-y-1">
              <div className="font-mono text-blue-600">17.24E, 13.06B, 17.15C</div>
              <div className="text-slate-500">Rack.Level+Position format</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">01A, 325B, 245D</div>
              <div className="text-slate-500">Position + Level format</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">01-A-1000A, 02-B-2500C</div>
              <div className="text-slate-500">Aisle-Rack-Position format</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">01-01-001A, 02-01-325B</div>
              <div className="text-slate-500">Standard warehouse format</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">A01-B02-P015, C03-D01-P999</div>
              <div className="text-slate-500">Letter-prefixed format</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">ZONE-A-001, AREA-B-125</div>
              <div className="text-slate-500">Zone-based locations</div>
            </div>
            <div className="space-y-1">
              <div className="font-mono text-blue-600">RECV-01, STAGE-01, DOCK-01</div>
              <div className="text-slate-500">Special work areas</div>
            </div>
          </div>
        </div>

        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <div className="font-medium">Troubleshooting suggestions:</div>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>Provide 4-6 examples that follow the same pattern</li>
                <li>Check that all examples use consistent separators (dashes, letters, numbers)</li>
                <li>Make sure examples are actual location codes you use in your warehouse</li>
                <li>If you have a unique format, try the manual configuration option below</li>
              </ul>
            </div>
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