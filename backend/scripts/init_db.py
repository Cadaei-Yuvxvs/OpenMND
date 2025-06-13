#!/usr/bin/env python3
"""
Database initialisation script for OpenMND
Creates all database tables defined in the models
"""

import sys
import os

# Add the backend directory to Python path
# This allows importing from the 'app' package
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

try:
    from app.models.research_paper import Base
    from app.core.database import engine
    print("Successfully imported modules")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Backend directory: {backend_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # List the tables that were created
        print("Created tables:")
        for table in Base.metadata.tables.keys():
            print(f"  - {table}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("Initialising OpenMND database...")
    create_tables()
    print("Database initialization complete!")

if __name__ == "__main__":
    main()
