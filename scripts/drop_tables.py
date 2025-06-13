#!/usr/bin/env python3
"""
Drop All Tables Script for Solar Platform
WARNING: This will delete ALL data in the database!
"""

import sys
import os
from sqlalchemy import create_engine, text, MetaData
import logging

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.core.config import settings
    from app.db.base import Base
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_engine():
    """Create database engine"""
    try:
        engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URL),
            pool_pre_ping=True,
            echo=False
        )
        logger.info("✅ Connected to database successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise

def drop_all_tables(engine):
    """Drop all tables in the database"""
    try:
        logger.info("🗑️ Dropping all tables...")
        
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                logger.info("No tables found to drop")
                return
            
            logger.info(f"Found tables to drop: {tables}")
            
            # Drop all tables with CASCADE to handle foreign key constraints
            for table in tables:
                try:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    logger.info(f"✅ Dropped table: {table}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not drop table {table}: {e}")
            
            conn.commit()
            
            # Verify all tables are dropped
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            
            remaining_tables = [row[0] for row in result.fetchall()]
            
            if remaining_tables:
                logger.warning(f"⚠️ Some tables still exist: {remaining_tables}")
            else:
                logger.info("✅ All tables dropped successfully!")
                
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        raise

def drop_using_metadata(engine):
    """Alternative method using SQLAlchemy metadata"""
    try:
        logger.info("🗑️ Dropping tables using metadata...")
        
        # Reflect existing database structure
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        if not metadata.tables:
            logger.info("No tables found in metadata")
            return
        
        logger.info(f"Tables found in metadata: {list(metadata.tables.keys())}")
        
        # Drop all tables
        metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped using metadata!")
        
    except Exception as e:
        logger.error(f"❌ Failed to drop tables using metadata: {e}")
        raise

def main():
    """Main function to drop all tables"""
    
    # Confirmation prompt
    print("⚠️ " + "="*60)
    print("WARNING: This will DELETE ALL TABLES and DATA!")
    print("="*64)
    print("This action cannot be undone!")
    print("Are you sure you want to continue?")
    
    confirm = input("Type 'YES' to confirm (case sensitive): ").strip()
    
    if confirm != "YES":
        print("❌ Operation cancelled")
        return
    
    try:
        logger.info("🚀 Starting table drop process...")
        
        # Create engine
        engine = create_database_engine()
        
        # Try both methods to ensure all tables are dropped
        try:
            drop_all_tables(engine)
        except Exception as e:
            logger.warning(f"⚠️ First method failed: {e}")
            logger.info("Trying alternative method...")
            drop_using_metadata(engine)
        
        logger.info("🎉 All tables dropped successfully!")
        logger.info("You can now run: python scripts/init_db.py")
        
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()