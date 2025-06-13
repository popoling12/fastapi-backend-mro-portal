#!/usr/bin/env python3
"""
Database Table Creation Script for Solar Platform
Creates all tables related to User Management System
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base import Base
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_engine():
    """Create database engine"""
    try:
        engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URL),
            pool_pre_ping=True,
            echo=True  # Set to False in production
        )
        logger.info(f"Connected to database: {settings.SQLALCHEMY_DATABASE_URL}")
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def create_tables(engine):
    """Create all tables"""
    try:
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        
        # Print created tables
        inspector = engine.dialect.get_table_names(engine.connect())
        logger.info(f"Created tables: {inspector}")
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def create_default_users(engine):
    """Create default system users"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Creating default users...")
        
        # Check if super admin exists
        existing_admin = db.query(User).filter(
            User.role == UserRole.SUPER_ADMIN
        ).first()
        
        if existing_admin:
            logger.info("Super admin already exists, skipping default user creation")
            return
        
        # Create Super Admin
        super_admin = User(
            email="admin@solar-platform.com",
            username="superadmin",
            hashed_password=get_password_hash("SuperAdmin123!"),
            first_name="System",
            last_name="Administrator",
            full_name="System Administrator",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP001",
            department="IT",
            position="System Administrator",
            company="Solar Platform Inc.",
            timezone="UTC",
            language="en",
            preferences={
                "theme": "dark",
                "dashboard_layout": "grid",
                "notifications_enabled": True
            },
            notification_settings={
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "work_order_notifications": True,
                "asset_alerts": True,
                "system_maintenance": True
            }
        )
        
        # Create Admin
        admin = User(
            email="admin@company.com",
            username="admin",
            hashed_password=get_password_hash("Admin123!"),
            first_name="Platform",
            last_name="Admin",
            full_name="Platform Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP002",
            department="Operations",
            position="Platform Administrator",
            company="Solar Platform Inc.",
            timezone="UTC",
            language="en"
        )
        
        # Create Plant Manager
        plant_manager = User(
            email="manager@plant.com",
            username="plantmanager",
            hashed_password=get_password_hash("Manager123!"),
            first_name="John",
            last_name="Smith",
            full_name="John Smith",
            role=UserRole.PLANT_MANAGER,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP003",
            department="Operations",
            position="Plant Manager",
            company="Solar Plant Co.",
            phone="+1-555-0101",
            mobile="+1-555-0102",
            timezone="America/New_York",
            language="en"
        )
        
        # Create Site Supervisor
        supervisor = User(
            email="supervisor@site.com",
            username="supervisor",
            hashed_password=get_password_hash("Supervisor123!"),
            first_name="Jane",
            last_name="Doe",
            full_name="Jane Doe",
            role=UserRole.SITE_SUPERVISOR,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP004",
            department="Field Operations",
            position="Site Supervisor",
            supervisor_id=None,  # Will be set after plant_manager is created
            company="Solar Plant Co.",
            phone="+1-555-0201",
            mobile="+1-555-0202",
            timezone="America/New_York",
            language="en"
        )
        
        # Create Technician
        technician = User(
            email="tech@field.com",
            username="technician",
            hashed_password=get_password_hash("Tech123!"),
            first_name="Mike",
            last_name="Johnson",
            full_name="Mike Johnson",
            role=UserRole.TECHNICIAN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP005",
            department="Field Operations",
            position="Field Technician",
            company="Solar Plant Co.",
            phone="+1-555-0301",
            mobile="+1-555-0302",
            timezone="America/New_York",
            language="en",
            skills={
                "electrical": "advanced",
                "mechanical": "intermediate",
                "solar_panels": "expert",
                "inverters": "advanced"
            },
            certifications={
                "electrical_license": "Valid until 2025-12-31",
                "safety_certification": "Valid until 2024-06-30"
            }
        )
        
        # Create Analyst
        analyst = User(
            email="analyst@data.com",
            username="analyst",
            hashed_password=get_password_hash("Analyst123!"),
            first_name="Sarah",
            last_name="Wilson",
            full_name="Sarah Wilson",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="EMP006",
            department="Analytics",
            position="Data Analyst",
            company="Solar Platform Inc.",
            phone="+1-555-0401",
            timezone="America/Los_Angeles",
            language="en"
        )
        
        # Create Viewer (Demo User)
        viewer = User(
            email="demo@viewer.com",
            username="demo",
            hashed_password=get_password_hash("Demo123!"),
            first_name="Demo",
            last_name="User",
            full_name="Demo User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            employee_id="DEMO001",
            department="Demo",
            position="Demo User",
            company="Demo Company",
            timezone="UTC",
            language="en"
        )
        
        # Add all users to database
        users = [super_admin, admin, plant_manager, supervisor, technician, analyst, viewer]
        
        for user in users:
            db.add(user)
        
        db.commit()
        
        # Set supervisor relationships
        plant_manager_id = db.query(User).filter(User.username == "plantmanager").first().id
        supervisor_record = db.query(User).filter(User.username == "supervisor").first()
        technician_record = db.query(User).filter(User.username == "technician").first()
        
        supervisor_record.supervisor_id = plant_manager_id
        technician_record.supervisor_id = supervisor_record.id
        
        db.commit()
        
        logger.info("✅ Default users created successfully!")
        
        # Print created users
        for user in users:
            logger.info(f"Created user: {user.email} ({user.role.value})")
        
    except Exception as e:
        logger.error(f"Failed to create default users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_tables(engine):
    """Verify that tables were created correctly"""
    try:
        logger.info("Verifying table structure...")
        
        with engine.connect() as conn:
            # Check users table
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            logger.info(f"Users table has {user_count} records")
            
            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            logger.info("Users table structure:")
            for col in columns:
                logger.info(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        logger.info("✅ Table verification completed!")
        
    except Exception as e:
        logger.error(f"Table verification failed: {e}")
        raise

def main():
    """Main function to create database tables and default data"""
    try:
        logger.info("🚀 Starting database setup...")
        
        # Create engine
        engine = create_database_engine()
        
        # Create tables
        create_tables(engine)
        
        # Create default users
        create_default_users(engine)
        
        # Verify tables
        verify_tables(engine)
        
        logger.info("🎉 Database setup completed successfully!")
        
        # Print connection info
        logger.info("\n" + "="*50)
        logger.info("DEFAULT LOGIN CREDENTIALS:")
        logger.info("="*50)
        logger.info("Super Admin:")
        logger.info("  Email: admin@solar-platform.com")
        logger.info("  Password: SuperAdmin123!")
        logger.info("\nAdmin:")
        logger.info("  Email: admin@company.com")
        logger.info("  Password: Admin123!")
        logger.info("\nDemo User:")
        logger.info("  Email: demo@viewer.com")
        logger.info("  Password: Demo123!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 