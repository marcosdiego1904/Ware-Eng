#!/usr/bin/env python3
"""
Deployment Script for Vercel
Handles database initialization for production deployments
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def deploy():
    """Main deployment function"""
    print("Starting deployment process...")
    
    # Import here to avoid issues during deployment
    from app import app
    from auto_migrate import auto_migrator
    
    with app.app_context():
        try:
            # Initialize database
            auto_migrator.ensure_database_ready()
            print("Deployment completed successfully!")
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    deploy()