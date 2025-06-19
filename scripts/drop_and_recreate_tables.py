#!/usr/bin/env python3
"""
Script to drop all tables and recreate them with the new asset model structure.
This will completely reset the database.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.asset import (
    Location, AssetTemplate, StoreInventory, Asset, AssetItem, AssetSensor
)
from app.models.user import User


def drop_all_tables():
    """Drop all tables from the database"""
    print("Dropping all tables...")
    
    # Create engine
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URL))
    
    # Get all table names
    with engine.connect() as conn:
        # Get all table names
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        
        print(f"Found tables: {tables}")
        
        # Drop all tables
        for table in tables:
            print(f"Dropping table: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        
        conn.commit()
    
    print("All tables dropped successfully!")


def create_all_tables():
    """Create all tables with the new structure"""
    print("Creating all tables...")
    
    # Create engine
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URL))
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("All tables created successfully!")


def main():
    """Main function to drop and recreate all tables"""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print("This script will:")
    print("1. Drop ALL existing tables")
    print("2. Create new tables with the updated schema")
    print("3. All data will be lost!")
    print("=" * 60)
    
    # Ask for confirmation
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        # Drop all tables
        drop_all_tables()
        
        # Create all tables
        create_all_tables()
        
        print("=" * 60)
        print("Database reset completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during database reset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 