#!/usr/bin/env python3
"""
API Usage Examples for Smart Configuration System

This script demonstrates how to use the Smart Configuration system APIs
for detecting location formats and creating templates with format configurations.

API Endpoints Demonstrated:
- POST /api/templates/detect-format    - Real-time format detection
- POST /api/templates/validate-format  - Format validation
- POST /api/templates                  - Template creation with format
- PUT  /api/templates/{id}            - Template update with format
"""

import requests
import json


class SmartFormatAPIExample:
    """
    Example client for Smart Configuration system APIs
    """
    
    def __init__(self, base_url="http://localhost:5000", auth_token=None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            })
    
    def detect_format(self, examples, warehouse_context=None):
        """
        Detect location format from examples
        
        Args:
            examples: List of location examples
            warehouse_context: Optional warehouse metadata
        
        Returns:
            API response with detection results
        """
        url = f"{self.base_url}/api/v1/templates/detect-format"
        payload = {
            'examples': examples
        }
        
        if warehouse_context:
            payload['warehouse_context'] = warehouse_context
        
        try:
            response = self.session.post(url, json=payload)
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.json().get('error') if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_format(self, format_config):
        """
        Validate a format configuration
        
        Args:
            format_config: Format configuration to validate
        
        Returns:
            API response with validation results
        """
        url = f"{self.base_url}/api/v1/templates/validate-format"
        payload = {
            'format_config': format_config
        }
        
        try:
            response = self.session.post(url, json=payload)
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.json().get('error') if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_template_with_format(self, template_data, location_format_data):
        """
        Create a warehouse template with location format configuration
        
        Args:
            template_data: Basic template information
            location_format_data: Location format configuration
        
        Returns:
            API response with created template
        """
        url = f"{self.base_url}/api/v1/templates"
        
        # Merge template data with location format
        payload = template_data.copy()
        payload['location_format'] = location_format_data
        
        try:
            response = self.session.post(url, json=payload)
            return {
                'success': response.status_code == 201,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 201 else None,
                'error': response.json().get('error') if response.status_code != 201 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_template_format(self, template_id, location_format_data):
        """
        Update template with new location format
        
        Args:
            template_id: Template ID to update
            location_format_data: New location format configuration
        
        Returns:
            API response with updated template
        """
        url = f"{self.base_url}/api/v1/templates/{template_id}"
        payload = {
            'location_format': location_format_data
        }
        
        try:
            response = self.session.put(url, json=payload)
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.json().get('error') if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def demo_format_detection():
    """Demonstrate format detection API"""
    print("="*60)
    print("DEMO: FORMAT DETECTION API")
    print("="*60)
    
    client = SmartFormatAPIExample()
    
    # Example 1: Position+Level format
    examples = ["010A", "325B", "245D", "156C"]
    warehouse_context = {
        'name': 'Main Warehouse',
        'description': 'Distribution center'
    }
    
    print(f"Detecting format for examples: {examples}")
    
    # Note: This would work with a live API server
    print("\nAPI Request:")
    print(f"POST /api/v1/templates/detect-format")
    print(f"Body: {json.dumps({'examples': examples, 'warehouse_context': warehouse_context}, indent=2)}")
    
    print("\nExpected Response (200 OK):")
    expected_response = {
        "success": True,
        "detection_result": {
            "detected_pattern": {
                "pattern_type": "position_level",
                "confidence": 0.95,
                "description": "Position+Level format (PPP+L) detected with 95.0% confidence"
            },
            "confidence": 0.95,
            "canonical_examples": [
                "010A → 01-01-010A",
                "325B → 01-01-325B",
                "245D → 01-01-245D"
            ],
            "analysis_summary": "Analyzed 4 location examples. Detected position_level format with 95.0% confidence.",
            "recommendations": [
                "This format will be converted to canonical format (01-01-PPPL) with default aisle=01, rack=01",
                "Good sample size provided - detection results should be reliable"
            ]
        },
        "format_config": {
            "pattern_type": "position_level",
            "confidence": 0.95,
            "canonical_converter": "01-01-{position:03d}{level}",
            "examples": ["010A", "325B", "245D", "156C"],
            "components": {
                "position_digits": 3,
                "level_format": "single_letter",
                "default_aisle": 1,
                "default_rack": 1
            }
        }
    }
    
    print(json.dumps(expected_response, indent=2))


def demo_template_creation_with_format():
    """Demonstrate template creation with format configuration"""
    print("\n" + "="*60)
    print("DEMO: TEMPLATE CREATION WITH FORMAT")
    print("="*60)
    
    client = SmartFormatAPIExample()
    
    template_data = {
        'name': 'Smart Warehouse Template',
        'description': 'Template with auto-detected location format',
        'num_aisles': 4,
        'racks_per_aisle': 2,
        'positions_per_rack': 50,
        'levels_per_position': 4,
        'level_names': 'ABCD',
        'default_pallet_capacity': 1,
        'is_public': True
    }
    
    # Option 1: Direct examples (will auto-detect)
    location_format_data = {
        'examples': ['010A', '325B', '245D']
    }
    
    print("Template Data:")
    print(json.dumps(template_data, indent=2))
    
    print("\nLocation Format Data (auto-detect from examples):")
    print(json.dumps(location_format_data, indent=2))
    
    print("\nAPI Request:")
    print(f"POST /api/v1/templates")
    
    full_payload = template_data.copy()
    full_payload['location_format'] = location_format_data
    
    print(f"Body: {json.dumps(full_payload, indent=2)}")
    
    print("\nExpected Response (201 Created):")
    expected_response = {
        "message": "Template created successfully",
        "template": {
            "id": 123,
            "name": "Smart Warehouse Template",
            "template_code": "WAR-4A2R-ABC",
            "location_format_config": {
                "pattern_type": "position_level",
                "confidence": 0.95
            },
            "format_confidence": 0.95,
            "format_examples": ["010A", "325B", "245D"],
            "has_location_format": True,
            "format_summary": "Position_level format (95.0% confidence, 3 examples)"
        }
    }
    
    print(json.dumps(expected_response, indent=2))


def demo_format_validation():
    """Demonstrate format validation API"""
    print("\n" + "="*60)
    print("DEMO: FORMAT VALIDATION API")
    print("="*60)
    
    format_config = {
        'pattern_type': 'position_level',
        'confidence': 0.95,
        'canonical_converter': '01-01-{position:03d}{level}',
        'examples': ['010A', '325B', '245D'],
        'components': {
            'position_digits': 3,
            'level_format': 'single_letter'
        }
    }
    
    print("Format Configuration to Validate:")
    print(json.dumps(format_config, indent=2))
    
    print("\nAPI Request:")
    print(f"POST /api/v1/templates/validate-format")
    print(f"Body: {json.dumps({'format_config': format_config}, indent=2)}")
    
    print("\nExpected Response (200 OK):")
    expected_response = {
        "success": True,
        "validation": {
            "valid": True,
            "errors": [],
            "warnings": []
        },
        "compatibility_check": {
            "canonical_service_available": True,
            "pattern_type": "position_level",
            "can_convert_to_canonical": True,
            "sample_conversions": [
                {
                    "original": "010A",
                    "canonical": "01-01-010A",
                    "success": True
                },
                {
                    "original": "325B",
                    "canonical": "01-01-325B",
                    "success": True
                }
            ]
        }
    }
    
    print(json.dumps(expected_response, indent=2))


def demo_complete_workflow():
    """Demonstrate complete workflow from detection to template creation"""
    print("\n" + "="*60)
    print("DEMO: COMPLETE WORKFLOW")
    print("="*60)
    
    print("SCENARIO: A user wants to create a template for their warehouse")
    print("They have location examples: ['010A', '325B', '245D', '156C']")
    
    print("\nSTEP 1: Detect format from examples")
    print("POST /api/v1/templates/detect-format")
    print("→ Response: position_level format detected (95% confidence)")
    
    print("\nSTEP 2: Validate the detected format")
    print("POST /api/v1/templates/validate-format")
    print("→ Response: Valid format, compatible with canonical system")
    
    print("\nSTEP 3: Create template with format configuration")
    print("POST /api/v1/templates")
    print("→ Response: Template created with smart location format")
    
    print("\nSTEP 4: Template is ready to use")
    print("→ Warehouse locations will automatically convert:")
    print("   010A → 01-01-010A")
    print("   325B → 01-01-325B")
    print("   245D → 01-01-245D")
    
    print("\n✅ Zero-friction location format configuration complete!")


def demo_error_handling():
    """Demonstrate error handling scenarios"""
    print("\n" + "="*60)
    print("DEMO: ERROR HANDLING")
    print("="*60)
    
    print("SCENARIO 1: Invalid examples")
    print("POST /api/v1/templates/detect-format")
    print("Body: {'examples': []}")
    print("Response (400): {'error': 'Location examples are required'}")
    
    print("\nSCENARIO 2: Inconsistent examples")
    print("POST /api/v1/templates/detect-format")
    print("Body: {'examples': ['invalid123', '!@#$%', 'abc']}")
    print("Response (200): {'detected_pattern': None, 'confidence': 0.0, 'recommendations': [...]}")
    
    print("\nSCENARIO 3: Invalid format configuration")
    print("POST /api/v1/templates/validate-format")
    print("Body: {'format_config': {'invalid': 'config'}}")
    print("Response (200): {'validation': {'valid': False, 'errors': ['Missing required field: pattern_type', ...]}}")
    
    print("\n✅ Robust error handling ensures reliable operation")


def main():
    """Main demo function"""
    print("🚀 SMART CONFIGURATION SYSTEM - API USAGE EXAMPLES")
    print("   Real-time location format detection via REST APIs")
    print("   Seamless integration with template creation workflow")
    
    demo_format_detection()
    demo_template_creation_with_format()
    demo_format_validation()
    demo_complete_workflow()
    demo_error_handling()
    
    print("\n" + "="*60)
    print("📚 INTEGRATION GUIDE")
    print("="*60)
    
    integration_notes = """
FRONTEND INTEGRATION:
1. Collect location examples from user input
2. Call /api/templates/detect-format in real-time as user types
3. Display confidence and pattern preview to user
4. Include format configuration in template creation request

BACKEND INTEGRATION:
1. Smart format detection is handled automatically in template APIs
2. Format configurations are stored in warehouse_template.location_format_config
3. Integration with existing CanonicalLocationService is seamless
4. No changes needed to existing location processing logic

WORKFLOW:
User pastes examples → Real-time detection → Format preview → Template creation → Ready to use!
"""
    
    print(integration_notes)
    
    print("🎉 API USAGE EXAMPLES COMPLETE")
    print("The Smart Configuration system is ready for frontend integration!")


if __name__ == "__main__":
    main()