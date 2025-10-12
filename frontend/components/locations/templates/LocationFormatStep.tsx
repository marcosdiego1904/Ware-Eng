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
    examples: "010A\n325B\n245D\n1230A\n5678D\n123456A"
  },
  {
    title: "Enterprise Scale Positions",
    description: "Large warehouse positions with 4+ digits",
    examples: "1000A\n2500B\n7890C\n15000A\n25000D"
  },
  {
    title: "Aisle-Rack-Position",
    description: "Multi-segment location codes for large warehouses",
    examples: "01-A-1000A\n02-B-2500C\n01-A-15000B\n03-C-7890A"
  },
  {
    title: "Zone + Sequential",
    description: "Zone identifier with sequential numbers",
    examples: "ZONE-A-001\nZONE-B-125\nZONE-C-1250\nZONE-A-5000"
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
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-slate-700 to-orange-700 shadow-xl mb-4">
          <MapPin className="h-8 w-8 text-orange-300" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Set Up Location Names</h3>
        <p className="text-base text-gray-600 max-w-lg mx-auto">
          Tell us how you currently name your storage locations, and we'll set up the same system for your warehouse
        </p>
      </div>

      {/* Format Application Status */}
      {formatApplied ? (
        <div className="bg-gradient-to-r from-emerald-50 to-slate-50 border border-emerald-200 rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-emerald-600 to-slate-700 shadow-lg">
              <CheckCircle className="h-4 w-4 text-emerald-200" />
            </div>
            <div>
              <div className="font-semibold text-slate-800">Perfect! Location system is ready</div>
              <div className="text-sm text-slate-600">We've learned your naming pattern and will use it throughout your warehouse</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-r from-blue-50 to-slate-50 border border-blue-200 rounded-lg p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-slate-700 shadow-lg">
              <Info className="h-4 w-4 text-blue-200" />
            </div>
            <div>
              <div className="font-semibold text-slate-800">How this works</div>
              <div className="text-sm text-slate-600 mt-1">
                Just show us 3-5 examples of how you name your storage spots (like A01, B15, or ZONE-A-001). 
                We'll figure out the pattern and set up your entire warehouse using the same system.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Example Input */}
      <div className="bg-gray-50 p-6 rounded-lg border">
        <div className="mb-4">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Show us your location names</h4>
          <p className="text-sm text-gray-600">
            Enter a few examples of how you currently label your storage spots
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="space-y-3">
            <Label htmlFor="examples" className="text-base font-medium text-gray-900">
              Your current location names
            </Label>
            <Textarea
              id="examples"
              value={examples}
              onChange={(e) => handleExamplesChange(e.target.value)}
              placeholder="A01&#10;B15&#10;C22&#10;D03&#10;A45"
              rows={6}
              className="font-mono text-base"
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {exampleList.length === 0 && "Enter 3-5 examples to get started"}
                {exampleList.length === 1 && "Great! Add 2-4 more examples"}
                {exampleList.length === 2 && "Perfect! Add 1-3 more examples"}
                {exampleList.length >= 3 && exampleList.length < 6 && "✅ Perfect! We're analyzing your pattern..."}
                {exampleList.length >= 6 && "✅ Excellent! That's plenty of examples"}
              </span>
              <span className="text-xs text-gray-500">One per line</span>
            </div>
          </div>

          {/* Quick Examples */}
          {examples.length === 0 && (
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-gray-50 px-4 text-gray-500">Or try one of these common formats</span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {EXAMPLE_SUGGESTIONS.map((suggestion, index) => (
                  <div
                    key={index}
                    className="cursor-pointer p-4 bg-white rounded-lg border hover:border-orange-200 hover:shadow-sm transition-all duration-200"
                    onClick={() => applySuggestion(suggestion)}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="font-medium text-gray-900 text-sm">{suggestion.title}</div>
                        <div className="text-xs text-orange-600 font-medium">Try this →</div>
                      </div>
                      <div className="text-xs text-gray-600">{suggestion.description}</div>
                      <div className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {suggestion.examples.split('\n').slice(0, 3).join(', ')}...
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detection Results */}
      {(detectionResult || loading || error) && exampleList.length >= 2 && (
        <div className="space-y-4">
          <div className="text-lg font-semibold text-gray-900">We found your pattern!</div>
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
      {exampleList.length === 1 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100">
              <Info className="h-4 w-4 text-yellow-600" />
            </div>
            <div>
              <div className="font-semibold text-yellow-900">Almost there!</div>
              <div className="text-sm text-yellow-700 mt-1">
                Add one or two more examples so we can understand your naming pattern better.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}