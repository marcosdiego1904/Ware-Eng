#!/usr/bin/env python3
"""
Simple server runner for testing the rules interface
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app

if __name__ == "__main__":
    print("\n" + "="*60)
    print("WAREHOUSE RULES MANAGEMENT SERVER STARTING")
    print("="*60)
    print(f"Rules Management Interface: http://localhost:5000/rules")
    print(f"API Endpoints: http://localhost:5000/api/v1/rules")
    print(f"Dashboard: http://localhost:5000/dashboard")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)