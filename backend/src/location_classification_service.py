"""
Location Classification Service for Overcapacity Rule Enhancement

This service implements the location type differentiation strategy outlined in the 
overcapacity enhancement documentation, providing business-context-aware location 
classification for optimized alerting.

Classification Strategy:
- Storage Locations (CRITICAL): Individual pallet tracking required
- Special Locations (WARNING): Area-level capacity management
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum


class LocationCategory(Enum):
    """Location categories for differentiated overcapacity handling"""
    STORAGE = "STORAGE"      # Critical inventory accuracy - individual pallet alerts
    SPECIAL = "SPECIAL"      # Operational space management - location-level alerts


class BusinessPriority(Enum):
    """Business priority mapping for location categories"""
    CRITICAL = "Very High"   # Storage locations - data integrity crisis
    WARNING = "High"         # Special locations - workflow efficiency concern


class LocationClassificationService:
    """
    Service for classifying warehouse locations into Storage vs Special categories
    based on business context and operational requirements.
    """
    
    # Location type mappings based on database location_type field
    STORAGE_LOCATION_TYPES = {
        'STORAGE',
        'FINAL'  # Final storage positions
    }
    
    SPECIAL_LOCATION_TYPES = {
        'RECEIVING',
        'STAGING', 
        'DOCK',
        'TRANSITIONAL',
        'AISLE',
        'BULK',
        'FLOOR'
    }
    
    # Pattern-based classification for locations without database entries
    STORAGE_PATTERNS = [
        re.compile(r'^\d+-\d+-\d+[A-Z]?$'),      # X-XX-XXX format (e.g., 1-01-01A)
        re.compile(r'^[A-Z]\d+-[A-Z]\d+-\d+$'),   # A1-B2-001 format
        re.compile(r'^\d+[A-Z]\d+[A-Z]\d+$'),     # 1A2B001 format
        re.compile(r'^USER_.*'),                   # User-defined storage
        re.compile(r'.*-RACK-.*'),                 # Rack positions
        re.compile(r'.*-SHELF-.*'),                # Shelf positions
    ]
    
    SPECIAL_PATTERNS = [
        re.compile(r'^(RECV|RECEIVING)-\d+$', re.IGNORECASE),    # RECV-01
        re.compile(r'^(STAGE|STAGING)-\d+$', re.IGNORECASE),     # STAGE-01  
        re.compile(r'^DOCK-\d+$', re.IGNORECASE),                # DOCK-01
        re.compile(r'^AISLE-\d+$', re.IGNORECASE),               # AISLE-01
        re.compile(r'^(BULK|FLOOR)-\d+$', re.IGNORECASE),        # BULK-01, FLOOR-01
        re.compile(r'^[A-Z]+-\d+$'),                             # Generic NAME-XX format
    ]

    def __init__(self):
        """Initialize the location classification service"""
        pass
    
    def classify_location(self, location_obj=None, location_code: str = "") -> Tuple[LocationCategory, BusinessPriority]:
        """
        Classify a location as Storage or Special based on business context.
        
        Args:
            location_obj: Database location object (if available)
            location_code: String location code for pattern matching
            
        Returns:
            Tuple of (LocationCategory, BusinessPriority)
        """
        
        # Priority 1: Use database location_type if available
        if location_obj and hasattr(location_obj, 'location_type'):
            location_type = location_obj.location_type
            
            if location_type in self.STORAGE_LOCATION_TYPES:
                return LocationCategory.STORAGE, BusinessPriority.CRITICAL
            elif location_type in self.SPECIAL_LOCATION_TYPES:
                return LocationCategory.SPECIAL, BusinessPriority.WARNING
        
        # Priority 2: Pattern-based classification
        location_upper = location_code.upper()
        
        # Check storage patterns first (more specific)
        for pattern in self.STORAGE_PATTERNS:
            if pattern.match(location_upper):
                return LocationCategory.STORAGE, BusinessPriority.CRITICAL
        
        # Check special area patterns
        for pattern in self.SPECIAL_PATTERNS:
            if pattern.match(location_upper):
                return LocationCategory.SPECIAL, BusinessPriority.WARNING
        
        # Priority 3: Keyword-based fallback classification
        storage_keywords = ['RACK', 'SHELF', 'STORAGE', 'POSITION']
        special_keywords = ['RECV', 'RECEIVING', 'STAGE', 'STAGING', 'DOCK', 'AISLE', 'BULK', 'FLOOR']
        
        for keyword in storage_keywords:
            if keyword in location_upper:
                return LocationCategory.STORAGE, BusinessPriority.CRITICAL
                
        for keyword in special_keywords:
            if keyword in location_upper:
                return LocationCategory.SPECIAL, BusinessPriority.WARNING
        
        # Default: Treat unknown locations as storage (conservative approach)
        # This ensures data integrity by requiring individual pallet investigation
        return LocationCategory.STORAGE, BusinessPriority.CRITICAL
    
    def get_alert_strategy(self, category: LocationCategory) -> Dict[str, Any]:
        """
        Get the appropriate alerting strategy for a location category.
        
        Args:
            category: LocationCategory enum value
            
        Returns:
            Dictionary with alerting configuration
        """
        
        if category == LocationCategory.STORAGE:
            return {
                'alert_level': 'individual_pallets',
                'priority': BusinessPriority.CRITICAL.value,
                'alert_template': 'Storage Location Accuracy Alert',
                'message_format': '{pallet_id} in overcapacity storage {location} ({count}/{capacity} pallets)',
                'business_justification': 'Inventory accuracy requires investigation of every pallet',
                'action_required': 'Investigate ALL pallets immediately'
            }
        else:  # SPECIAL
            return {
                'alert_level': 'location_summary',
                'priority': BusinessPriority.WARNING.value, 
                'alert_template': 'Operational Area Capacity Monitor',
                'message_format': '{location} at {percentage}% capacity ({count}/{capacity} pallets) - expedite processing',
                'business_justification': 'Space management focus, no individual pallet investigation needed',
                'action_required': 'Monitor area and expedite processing'
            }
    
    def analyze_location_distribution(self, location_counts: Dict[str, int], 
                                   location_finder_func) -> Dict[str, Any]:
        """
        Analyze the distribution of overcapacity locations by category.
        
        Args:
            location_counts: Dictionary of location -> pallet count
            location_finder_func: Function to find location objects by code
            
        Returns:
            Analysis summary with storage vs special breakdown
        """
        
        analysis = {
            'total_locations': len(location_counts),
            'storage_locations': [],
            'special_locations': [],
            'storage_count': 0,
            'special_count': 0,
            'expected_alert_reduction': 0
        }
        
        total_pallets_affected = 0
        storage_pallets = 0
        special_pallets = 0
        
        for location, count in location_counts.items():
            location_obj = location_finder_func(str(location))
            category, priority = self.classify_location(location_obj, str(location))
            
            location_info = {
                'location': location,
                'pallet_count': count,
                'category': category.value,
                'priority': priority.value
            }
            
            if category == LocationCategory.STORAGE:
                analysis['storage_locations'].append(location_info)
                analysis['storage_count'] += 1
                storage_pallets += count
            else:
                analysis['special_locations'].append(location_info)
                analysis['special_count'] += 1
                special_pallets += count
            
            total_pallets_affected += count
        
        # Calculate expected alert reduction
        # Storage: individual alerts (no change)
        # Special: location-level alerts (significant reduction)
        current_alerts = total_pallets_affected
        new_alerts = storage_pallets + analysis['special_count']  # Individual + location-level
        
        if current_alerts > 0:
            analysis['expected_alert_reduction'] = ((current_alerts - new_alerts) / current_alerts) * 100
        
        analysis['alert_summary'] = {
            'current_system': current_alerts,
            'enhanced_system': new_alerts,
            'reduction_count': current_alerts - new_alerts,
            'reduction_percentage': analysis['expected_alert_reduction']
        }
        
        return analysis