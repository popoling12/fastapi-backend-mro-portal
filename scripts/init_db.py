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

try:
    from app.core.config import settings
    from app.db.base import Base
    from app.models.user import User, UserRole, UserStatus
    from app.core.security import get_password_hash
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
            echo=False  # Set to True for SQL debugging
        )
        logger.info("✅ Connected to database successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise

def create_tables(engine):
    """Create all tables"""
    try:
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        
        # Print created tables
        with engine.connect() as conn:
            inspector_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            result = conn.execute(inspector_query)
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Available tables: {tables}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

def create_default_users(engine):
    """Create default system users"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Creating default users...")
        
        # Check if super admin exists
        existing_admin = db.query(User).filter(User.email == "admin@solar-platform.com").first()
        
        if existing_admin:
            logger.info("Super admin already exists, skipping default user creation")
            return
        
        # Define default users with manual data (avoiding schema dependency)
        default_users_data = [
            {
                "email": "admin@solar-platform.com",
                "username": "superadmin",
                "password": "SuperAdmin123!",
                "first_name": "System",
                "last_name": "Administrator",
                "role": UserRole.SUPER_ADMIN,
                "employee_id": "EMP001",
                "department": "IT",
                "position": "System Administrator",
                "company": "Solar Platform Inc.",
                "phone": "+1-555-0001",
                "mobile": "+1-555-0002",
                "description": "Super Administrator"
            },
            {
                "email": "admin@company.com",
                "username": "admin",
                "password": "Admin123!",
                "first_name": "Platform",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
                "employee_id": "EMP002",
                "department": "Operations",
                "position": "Platform Administrator",
                "company": "Solar Platform Inc.",
                "phone": "+1-555-0011",
                "mobile": "+1-555-0012",
                "description": "Platform Administrator"
            },
            {
                "email": "manager@plant.com",
                "username": "plantmanager",
                "password": "Manager123!",
                "first_name": "John",
                "last_name": "Smith",
                "role": UserRole.PLANT_MANAGER,
                "employee_id": "EMP003",
                "department": "Operations",
                "position": "Plant Manager",
                "company": "Solar Plant Co.",
                "phone": "+1-555-0101",
                "mobile": "+1-555-0102",
                "timezone": "America/New_York",
                "description": "Plant Manager"
            },
            {
                "email": "supervisor@site.com",
                "username": "supervisor",
                "password": "Supervisor123!",
                "first_name": "Jane",
                "last_name": "Doe",
                "role": UserRole.SITE_SUPERVISOR,
                "employee_id": "EMP004",
                "department": "Field Operations",
                "position": "Site Supervisor",
                "company": "Solar Plant Co.",
                "phone": "+1-555-0201",
                "mobile": "+1-555-0202",
                "timezone": "America/New_York",
                "description": "Site Supervisor"
            },
            {
                "email": "tech@field.com",
                "username": "technician",
                "password": "Tech123!",
                "first_name": "Mike",
                "last_name": "Johnson",
                "role": UserRole.TECHNICIAN,
                "employee_id": "EMP005",
                "department": "Field Operations",
                "position": "Field Technician",
                "company": "Solar Plant Co.",
                "phone": "+1-555-0301",
                "mobile": "+1-555-0302",
                "timezone": "America/New_York",
                "description": "Field Technician"
            },
            {
                "email": "analyst@data.com",
                "username": "analyst",
                "password": "Analyst123!",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "role": UserRole.ANALYST,
                "employee_id": "EMP006",
                "department": "Analytics",
                "position": "Data Analyst",
                "company": "Solar Platform Inc.",
                "phone": "+1-555-0401",
                "mobile": "+1-555-0402",
                "timezone": "America/Los_Angeles",
                "description": "Data Analyst"
            },
            {
                "email": "operator@control.com",
                "username": "operator",
                "password": "Operator123!",
                "first_name": "David",
                "last_name": "Brown",
                "role": UserRole.OPERATOR,
                "employee_id": "EMP007",
                "department": "Control Room",
                "position": "Control Room Operator",
                "company": "Solar Plant Co.",
                "phone": "+1-555-0501",
                "mobile": "+1-555-0502",
                "timezone": "America/New_York",
                "description": "Control Room Operator"
            },
            {
                "email": "demo@viewer.com",
                "username": "demo",
                "password": "Demo123!",
                "first_name": "Demo",
                "last_name": "User",
                "role": UserRole.VIEWER,
                "employee_id": "DEMO001",
                "department": "Demo",
                "position": "Demo User",
                "company": "Demo Company",
                "description": "Demo User"
            },
            {
                "email": "customer@client.com",
                "username": "customer",
                "password": "Customer123!",
                "first_name": "Alex",
                "last_name": "Client",
                "role": UserRole.CUSTOMER,
                "employee_id": "CUST001",
                "department": "External",
                "position": "Customer Representative",
                "company": "Client Company",
                "phone": "+1-555-0601",
                "description": "Customer"
            },
            {
                "email": "contractor@external.com",
                "username": "contractor",
                "password": "Contractor123!",
                "first_name": "Mark",
                "last_name": "External",
                "role": UserRole.CONTRACTOR,
                "employee_id": "CONT001",
                "department": "External",
                "position": "External Contractor",
                "company": "Contractor Inc.",
                "phone": "+1-555-0701",
                "description": "External Contractor"
            }
        ]
        
        created_users = []
        
        # Create all users
        for user_data in default_users_data:
            try:
                # Hash password
                hashed_password = get_password_hash(user_data["password"])
                
                # Create full_name
                full_name = f"{user_data['first_name']} {user_data['last_name']}".strip()
                
                # Create user object
                db_user = User(
                    email=user_data["email"],
                    username=user_data.get("username"),
                    hashed_password=hashed_password,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    full_name=full_name,
                    phone=user_data.get("phone"),
                    mobile=user_data.get("mobile"),
                    role=user_data["role"],
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    is_verified=True,  # Set to True for demo
                    employee_id=user_data.get("employee_id"),
                    department=user_data.get("department"),
                    position=user_data.get("position"),
                    company=user_data.get("company"),
                    timezone=user_data.get("timezone", "UTC"),
                    language="en",
                    preferences={
                        "theme": "light",
                        "dashboard_layout": "grid",
                        "notifications_enabled": True
                    },
                    notification_settings={
                        "email_enabled": True,
                        "sms_enabled": False,
                        "push_enabled": True,
                        "work_order_notifications": True,
                        "asset_alerts": True,
                        "system_maintenance": True,
                        "daily_reports": False
                    }
                )
                
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                created_users.append((db_user, user_data["description"]))
                logger.info(f"✅ Created {user_data['description']}: {user_data['email']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create {user_data['description']}: {e}")
                db.rollback()
                continue
        
        # Set supervisor relationships after all users are created
        try:
            # Get users for setting relationships  
            plant_manager = db.query(User).filter(User.email == "manager@plant.com").first()
            supervisor = db.query(User).filter(User.email == "supervisor@site.com").first()
            technician = db.query(User).filter(User.email == "tech@field.com").first()
            operator = db.query(User).filter(User.email == "operator@control.com").first()
            
            if plant_manager and supervisor:
                supervisor.supervisor_id = plant_manager.id
                db.commit()
                logger.info(f"✅ Set {supervisor.full_name} supervisor to {plant_manager.full_name}")
            
            if supervisor and technician:
                technician.supervisor_id = supervisor.id
                db.commit()
                logger.info(f"✅ Set {technician.full_name} supervisor to {supervisor.full_name}")
            
            if plant_manager and operator:
                operator.supervisor_id = plant_manager.id
                db.commit()
                logger.info(f"✅ Set {operator.full_name} supervisor to {plant_manager.full_name}")
                
        except Exception as e:
            logger.error(f"⚠️ Failed to set supervisor relationships: {e}")
        
        # Add additional user data (skills, certifications) for some users
        try:
            technician = db.query(User).filter(User.email == "tech@field.com").first()
            if technician:
                technician.skills = {
                    "electrical": "advanced",
                    "mechanical": "intermediate", 
                    "solar_panels": "expert",
                    "inverters": "advanced",
                    "troubleshooting": "expert"
                }
                technician.certifications = {
                    "electrical_license": "Valid until 2025-12-31",
                    "safety_certification": "Valid until 2024-06-30",
                    "solar_certification": "Valid until 2026-03-15"
                }
                technician.emergency_contact = {
                    "name": "Lisa Johnson",
                    "relationship": "Sister",
                    "phone": "+1-555-0303"
                }
                db.commit()
                logger.info(f"✅ Added skills and certifications for {technician.full_name}")
            
            plant_manager = db.query(User).filter(User.email == "manager@plant.com").first()
            if plant_manager:
                plant_manager.certifications = {
                    "management_certification": "Valid until 2025-08-30",
                    "safety_manager": "Valid until 2024-12-31"
                }
                plant_manager.emergency_contact = {
                    "name": "Sarah Smith",
                    "relationship": "Spouse",
                    "phone": "+1-555-0103",
                    "email": "sarah.smith@email.com"
                }
                db.commit()
                logger.info(f"✅ Added certifications for {plant_manager.full_name}")
                
        except Exception as e:
            logger.error(f"⚠️ Failed to add additional user data: {e}")
        
        logger.info(f"✅ Successfully created {len(created_users)} default users!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create default users: {e}")
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
            
            # Verify user roles distribution
            result = conn.execute(text("""
                SELECT role, COUNT(*) as count 
                FROM users 
                WHERE deleted_at IS NULL
                GROUP BY role 
                ORDER BY role
            """))
            
            roles = result.fetchall()
            logger.info("User roles distribution:")
            for role in roles:
                logger.info(f"  {role[0]}: {role[1]} users")
            
            # Check supervisor relationships
            result = conn.execute(text("""
                SELECT 
                    u1.full_name as user_name,
                    u1.role as user_role,
                    u2.full_name as supervisor_name,
                    u2.role as supervisor_role
                FROM users u1 
                LEFT JOIN users u2 ON u1.supervisor_id = u2.id
                WHERE u1.supervisor_id IS NOT NULL
                ORDER BY u1.full_name
            """))
            
            relationships = result.fetchall()
            if relationships:
                logger.info("Supervisor relationships:")
                for rel in relationships:
                    logger.info(f"  {rel[0]} ({rel[1]}) → {rel[2]} ({rel[3]})")
        
        logger.info("✅ Table verification completed!")
        
    except Exception as e:
        logger.error(f"❌ Table verification failed: {e}")
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
        logger.info("\n" + "="*60)
        logger.info("DEFAULT LOGIN CREDENTIALS:")
        logger.info("="*60)
        logger.info("Super Admin:")
        logger.info("  Email: admin@solar-platform.com")
        logger.info("  Password: SuperAdmin123!")
        logger.info("\nPlatform Admin:")
        logger.info("  Email: admin@company.com")
        logger.info("  Password: Admin123!")
        logger.info("\nPlant Manager:")
        logger.info("  Email: manager@plant.com")
        logger.info("  Password: Manager123!")
        logger.info("\nSite Supervisor:")
        logger.info("  Email: supervisor@site.com")
        logger.info("  Password: Supervisor123!")
        logger.info("\nTechnician:")
        logger.info("  Email: tech@field.com")
        logger.info("  Password: Tech123!")
        logger.info("\nAnalyst:")
        logger.info("  Email: analyst@data.com")
        logger.info("  Password: Analyst123!")
        logger.info("\nOperator:")
        logger.info("  Email: operator@control.com")
        logger.info("  Password: Operator123!")
        logger.info("\nDemo User (Viewer):")
        logger.info("  Email: demo@viewer.com")
        logger.info("  Password: Demo123!")
        logger.info("\nCustomer:")
        logger.info("  Email: customer@client.com")
        logger.info("  Password: Customer123!")
        logger.info("\nContractor:")
        logger.info("  Email: contractor@external.com")
        logger.info("  Password: Contractor123!")
        logger.info("="*60)
        logger.info("\n🌐 You can now start the FastAPI server with:")
        logger.info("uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()