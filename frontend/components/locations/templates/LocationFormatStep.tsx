'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  MapPin, 
  Sparkles, 
  Info,
  Copy,
  FileText,
  CheckCircle
} from 'lucide-react';
import { standaloneTemplateAPI, type FormatDetectionResult } from '@/lib/standalone-template-api';
import { FormatDetectionDisplay } from './FormatDetectionDisplay';

interface LocationFormatStepProps {
  onFormatDetected: (formatConfig: object, patternName: string, examples: string[]) => void;
  onManualConfiguration?: () => void;
  initialExamples?: string;
  onFormatApplied?: (applied: boolean) => void; // New callback to notify parent about format application status
}

// Debounce hook for API calls
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

const EXAMPLE_SUGGESTIONS = [
  {
    title: "Position + Level Format",
    description: "Position number followed by level letter",
    examples: "010A\n325B\n245D\n100C\n005A"
  },
  {
    title: "Aisle-Rack-Position",
    description: "Multi-segment location codes",
    examples: "A01-R02-P15\nB05-R01-P03\nC12-R03-P25"
  },
  {
    title: "Zone + Sequential",
    description: "Zone identifier with sequential numbers",
    examples: "ZONE-A-001\nZONE-B-125\nZONE-C-075"
  }
];

export function LocationFormatStep({
  onFormatDetected,
  onManualConfiguration,
  initialExamples = "",
  onFormatApplied
}: LocationFormatStepProps) {
  const [examples, setExamples] = useState(initialExamples);
  const [detectionResult, setDetectionResult] = useState<FormatDetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formatApplied, setFormatApplied] = useState(false);
  
  // Debounce the examples input to avoid excessive API calls
  const debouncedExamples = useDebounce(examples, 800);
  
  const parseExamples = useCallback((text: string): string[] => {
    return text
      .split(/[\n,;]/)
      .map(ex => ex.trim())
      .filter(ex => ex.length > 0);
  }, []);

  const detectFormat = useCallback(async (exampleList: string[]) => {
    if (exampleList.length < 2) {
      setDetectionResult(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await standaloneTemplateAPI.detectLocationFormat(exampleList);
      setDetectionResult(result);
    } catch (err: any) {
      console.error('Format detection failed:', err);
      setError(err?.response?.data?.error || 'Failed to detect format. Please try again.');
      setDetectionResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Trigger format detection when debounced examples change
  useEffect(() => {
    const exampleList = parseExamples(debouncedExamples);
    detectFormat(exampleList);
  }, [debouncedExamples, parseExamples, detectFormat]);

  // Reset format applied state when user manually changes examples
  const handleExamplesChange = (value: string) => {
    setExamples(value);
    // Reset format applied state when user changes examples
    if (formatApplied && value !== examples) {
      setFormatApplied(false);
      onFormatApplied?.(false);
    }
  };

  // Note: Auto-application removed to prevent wizard state conflicts
  // High-confidence detections are now handled through improved UI feedback

  const handleAcceptFormat = () => {
    if (detectionResult && detectionResult.detected && detectionResult.format_config) {
      const exampleList = parseExamples(examples);
      onFormatDetected(detectionResult.format_config, detectionResult.pattern_name, exampleList);
      setFormatApplied(true);
      onFormatApplied?.(true);
    }
  };

  const handleManualConfiguration = () => {
    if (onManualConfiguration) {
      onManualConfiguration();
    } else {
      // TODO: Implement default manual configuration flow
      console.log('Manual configuration requested');
    }
  };


  const applySuggestion = (suggestion: typeof EXAMPLE_SUGGESTIONS[0]) => {
    setExamples(suggestion.examples);
  };

  const exampleList = parseExamples(examples);

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <MapPin className="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 className="text-lg font-semibold">Smart Location Format</h3>
        <p className="text-sm text-muted-foreground">
          Paste your location examples and we'll automatically detect the pattern
        </p>
      </div>

      {/* Format Application Status */}
      {formatApplied ? (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <strong>Format Configuration Applied!</strong> Your template will use the detected location format pattern.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert>
          <Sparkles className="h-4 w-4" />
          <AlertDescription>
            <strong>How it works:</strong> Enter 3-10 location examples from your warehouse. 
            Our AI will detect the pattern for your template.
          </AlertDescription>
        </Alert>
      )}

      {/* Example Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Location Examples
          </CardTitle>
          <CardDescription>
            Paste your location codes (one per line or comma-separated)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="examples">Your Location Codes</Label>
            <Textarea
              id="examples"
              value={examples}
              onChange={(e) => handleExamplesChange(e.target.value)}
              placeholder="010A&#10;325B&#10;245D&#10;100C&#10;005A"
              rows={6}
              className="font-mono text-sm"
            />
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>
                {exampleList.length} example{exampleList.length !== 1 ? 's' : ''} entered
                {exampleList.length >= 2 && ' • Detection active'}
              </span>
              <span>Supports multiple formats: newlines, commas, semicolons</span>
            </div>
          </div>

          {/* Quick Examples */}
          {examples.length === 0 && (
            <div className="space-y-3">
              <div className="text-sm font-medium">Quick Examples</div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {EXAMPLE_SUGGESTIONS.map((suggestion, index) => (
                  <Card
                    key={index}
                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => applySuggestion(suggestion)}
                  >
                    <CardContent className="p-3">
                      <div className="space-y-1">
                        <div className="text-sm font-medium">{suggestion.title}</div>
                        <div className="text-xs text-muted-foreground">
                          {suggestion.description}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-primary">
                          <Copy className="h-3 w-3" />
                          Click to use
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detection Results */}
      {(detectionResult || loading || error) && (
        <div className="space-y-4">
          <div className="text-sm font-medium">Detection Results</div>
          <FormatDetectionDisplay
            result={detectionResult}
            loading={loading}
            error={error}
            originalExamples={exampleList}
            onAcceptFormat={handleAcceptFormat}
            onManualConfiguration={handleManualConfiguration}
            isApplied={formatApplied}
          />
        </div>
      )}

      {/* Help Text */}
      {exampleList.length < 2 && examples.length > 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Please provide at least 2 valid location examples for pattern detection.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}