#!/usr/bin/env python3
"""
Script to create test database for running tests
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def create_test_database():
    """Create test database if it doesn't exist"""
    # Connect to default postgres database
    default_db_url = str(settings.SQLALCHEMY_DATABASE_URL).replace(
        settings.POSTGRES_DB,
        "postgres"
    )
    engine = create_engine(default_db_url)
    
    # Create test database
    test_db_name = f"{settings.POSTGRES_DB}_test"
    
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{test_db_name}'")
        )
        database_exists = result.scalar() is not None
        
        if not database_exists:
            # Close all connections to postgres database
            conn.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'postgres'
                AND pid <> pg_backend_pid()
            """))
            
            # Create test database
            conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))
            print(f"✅ Created test database: {test_db_name}")
        else:
            print(f"✅ Test database {test_db_name} already exists")

if __name__ == "__main__":
    try:
        create_test_database()
    except Exception as e:
        print(f"❌ Failed to create test database: {e}")
        sys.exit(1) 