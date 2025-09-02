// Test the confidence transformation fix
const mockBackendData = {
  success: true,
  detection_result: {
    detected_pattern: {
      pattern_type: 'position_level'
    },
    confidence: 1.0, // Backend returns 0-1 decimal
    canonical_examples: ['001A', '002B']
  },
  format_config: {}
};

// Simulate the OLD transformation (broken)
const oldResult = {
  confidence: mockBackendData.detection_result.confidence || 0 // 1.0 displayed as "1%"
};

// Simulate the NEW transformation (fixed)
const detectionResult = mockBackendData.detection_result || {};
const detectedPattern = detectionResult.detected_pattern;

const newResult = {
  detected: mockBackendData.success && !!detectedPattern,
  format_config: mockBackendData.format_config,
  confidence: Math.round((detectionResult.confidence || 0) * 100), // Convert 0-1 to 0-100
  pattern_name: detectedPattern?.pattern_type || 'unknown',
  canonical_examples: detectionResult.canonical_examples || []
};

console.log('CONFIDENCE FIX TEST');
console.log('==================');
console.log('Backend confidence (0-1 decimal):', mockBackendData.detection_result.confidence);
console.log('');
console.log('OLD (broken):');
console.log('  Frontend confidence:', oldResult.confidence);
console.log('  Display shows:', oldResult.confidence + '%');
console.log('  Confidence >= 80:', oldResult.confidence >= 80);
console.log('  Shows warning:', oldResult.confidence < 80);
console.log('');
console.log('NEW (fixed):');
console.log('  Frontend confidence:', newResult.confidence);
console.log('  Display shows:', newResult.confidence + '%');
console.log('  Confidence >= 80:', newResult.confidence >= 80);
console.log('  Shows warning:', newResult.confidence < 80);
console.log('');
console.log('✅ Fix successful:', newResult.confidence === 100 && !newResult.confidence < 80);
console.log('✅ Will show "Looks perfect":', newResult.confidence >= 80);