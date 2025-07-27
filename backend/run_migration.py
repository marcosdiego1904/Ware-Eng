"""
Migration runner with proper environment setup
"""

import os
import sys

# Set environment variables
os.environ['FLASK_SECRET_KEY'] = 'migration-secret-key-temp'
os.environ['DATABASE_URL'] = ''  # Use SQLite for development

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run migration
from migrate import DatabaseMigrator

if __name__ == '__main__':
    print("Warehouse Rules System Database Migration")
    print("This will add new tables and migrate existing data.")
    print("Your existing data will be backed up before any changes.")
    print("\nProceeding with migration...")
    
    # Create migrator and run
    migrator = DatabaseMigrator()
    success = migrator.run_full_migration()
    
    if success:
        print("\n🎉 Ready to start using the new rules system!")
    else:
        print("\n⚠️  Please check the errors above and try again.")