#!/usr/bin/env python3
"""
Database Asset Initialization Script for Solar Platform
Creates and populates the assets table with sample data
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
    from app.models.asset import Asset, AssetType, AssetStatus
    from app.models.user import User
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

def create_assets_table(engine):
    """Create assets table if it doesn't exist"""
    try:
        logger.info("Creating assets table...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Assets table created successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to create assets table: {e}")
        raise

def create_sample_assets(engine):
    """Create sample assets data"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("Creating sample assets...")
        
        # Get admin user for created_by
        admin = db.query(User).filter(User.email == "admin@solar-platform.com").first()
        if not admin:
            raise Exception("Admin user not found")
        
        # Define sample assets data
        sample_assets = [
            {
                "name": "Solar Valley Plant",
                "code": "PLT001",
                "asset_type": AssetType.PLANT,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "SolarTech Inc.",
                "model_number": "ST-PLANT-1000",
                "config": {
                    "capacity_mw": 100,
                    "total_panels": 250000,
                    "total_inverters": 1000
                }
            },
            {
                "name": "North Block",
                "code": "SUB001",
                "asset_type": AssetType.SUB_PLANT,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - North",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "SolarTech Inc.",
                "model_number": "ST-SUB-250",
                "config": {
                    "capacity_mw": 25,
                    "total_panels": 62500,
                    "total_inverters": 250
                }
            },
            {
                "name": "South Block",
                "code": "SUB002",
                "asset_type": AssetType.SUB_PLANT,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - South",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "SolarTech Inc.",
                "model_number": "ST-SUB-250",
                "config": {
                    "capacity_mw": 25,
                    "total_panels": 62500,
                    "total_inverters": 250
                }
            },
            {
                "name": "Inverter Array 1",
                "code": "INV001",
                "asset_type": AssetType.INVERTER,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - North Block",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "PowerTech",
                "model_number": "PT-1000",
                "serial_number": "INV2020-001",
                "config": {
                    "capacity_kw": 1000,
                    "efficiency": 0.98,
                    "max_voltage": 1000,
                    "max_current": 100
                },
                "realtime_data_tag": "PLT001/SUB001/INV001"
            },
            {
                "name": "String 1",
                "code": "STR001",
                "asset_type": AssetType.STRING,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - North Block",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "SolarTech Inc.",
                "model_number": "ST-STRING-100",
                "config": {
                    "panel_count": 100,
                    "max_voltage": 1000,
                    "max_current": 10
                },
                "realtime_data_tag": "PLT001/SUB001/STR001"
            },
            {
                "name": "Panel Array 1",
                "code": "PAN001",
                "asset_type": AssetType.PANEL,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - North Block",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "SolarTech Inc.",
                "model_number": "ST-PANEL-400",
                "serial_number": "PAN2020-001",
                "config": {
                    "capacity_w": 400,
                    "efficiency": 0.21,
                    "max_voltage": 40,
                    "max_current": 10
                }
            },
            {
                "name": "Weather Station 1",
                "code": "SEN001",
                "asset_type": AssetType.SENSOR,
                "status": AssetStatus.ACTIVE,
                "location": "Solar Valley, CA - North Block",
                "installation_date": datetime(2020, 1, 1),
                "manufacturer": "WeatherTech",
                "model_number": "WT-100",
                "serial_number": "WS2020-001",
                "config": {
                    "sensor_types": ["temperature", "humidity", "wind_speed", "irradiance"],
                    "update_interval": 60,
                    "battery_life": 365
                },
                "realtime_data_tag": "PLT001/SUB001/SEN001"
            }
        ]
        
        created_assets = []
        
        # Create all assets
        for asset_data in sample_assets:
            try:
                # Create asset object
                db_asset = Asset(
                    name=asset_data["name"],
                    code=asset_data["code"],
                    asset_type=asset_data["asset_type"],
                    status=asset_data["status"],
                    location=asset_data["location"],
                    installation_date=asset_data["installation_date"],
                    manufacturer=asset_data["manufacturer"],
                    model_number=asset_data["model_number"],
                    serial_number=asset_data.get("serial_number"),
                    config=asset_data["config"],
                    realtime_data_tag=asset_data.get("realtime_data_tag"),
                    created_by_id=admin.id
                )
                
                db.add(db_asset)
                db.commit()
                db.refresh(db_asset)
                
                created_assets.append(db_asset)
                logger.info(f"✅ Created asset: {asset_data['name']} ({asset_data['code']})")
                
            except Exception as e:
                logger.error(f"❌ Failed to create asset {asset_data['name']}: {e}")
                db.rollback()
                continue
        
        # Set parent-child relationships
        try:
            # Get assets for setting relationships
            plant = db.query(Asset).filter(Asset.code == "PLT001").first()
            north_block = db.query(Asset).filter(Asset.code == "SUB001").first()
            south_block = db.query(Asset).filter(Asset.code == "SUB002").first()
            inverter = db.query(Asset).filter(Asset.code == "INV001").first()
            string = db.query(Asset).filter(Asset.code == "STR001").first()
            panel = db.query(Asset).filter(Asset.code == "PAN001").first()
            sensor = db.query(Asset).filter(Asset.code == "SEN001").first()
            
            if plant and north_block:
                north_block.parent_id = plant.id
                db.commit()
                logger.info(f"✅ Set {north_block.name} parent to {plant.name}")
            
            if plant and south_block:
                south_block.parent_id = plant.id
                db.commit()
                logger.info(f"✅ Set {south_block.name} parent to {plant.name}")
            
            if north_block and inverter:
                inverter.parent_id = north_block.id
                db.commit()
                logger.info(f"✅ Set {inverter.name} parent to {north_block.name}")
            
            if inverter and string:
                string.parent_id = inverter.id
                db.commit()
                logger.info(f"✅ Set {string.name} parent to {inverter.name}")
            
            if string and panel:
                panel.parent_id = string.id
                db.commit()
                logger.info(f"✅ Set {panel.name} parent to {string.name}")
            
            if north_block and sensor:
                sensor.parent_id = north_block.id
                db.commit()
                logger.info(f"✅ Set {sensor.name} parent to {north_block.name}")
                
        except Exception as e:
            logger.error(f"⚠️ Failed to set asset relationships: {e}")
        
        logger.info(f"✅ Successfully created {len(created_assets)} sample assets!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample assets: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_assets(engine):
    """Verify that assets were created correctly"""
    try:
        logger.info("Verifying assets...")
        
        with engine.connect() as conn:
            # Check assets table
            result = conn.execute(text("SELECT COUNT(*) FROM assets"))
            asset_count = result.scalar()
            logger.info(f"Assets table has {asset_count} records")
            
            # Verify asset types distribution
            result = conn.execute(text("""
                SELECT asset_type, COUNT(*) as count 
                FROM assets 
                GROUP BY asset_type 
                ORDER BY asset_type
            """))
            
            types = result.fetchall()
            logger.info("Asset types distribution:")
            for type_ in types:
                logger.info(f"  {type_[0]}: {type_[1]} assets")
            
            # Check parent-child relationships
            result = conn.execute(text("""
                SELECT 
                    a1.name as asset_name,
                    a1.asset_type as asset_type,
                    a2.name as parent_name,
                    a2.asset_type as parent_type
                FROM assets a1 
                LEFT JOIN assets a2 ON a1.parent_id = a2.id
                WHERE a1.parent_id IS NOT NULL
                ORDER BY a1.name
            """))
            
            relationships = result.fetchall()
            if relationships:
                logger.info("Asset relationships:")
                for rel in relationships:
                    logger.info(f"  {rel[0]} ({rel[1]}) → {rel[2]} ({rel[3]})")
        
        logger.info("✅ Asset verification completed!")
        
    except Exception as e:
        logger.error(f"❌ Asset verification failed: {e}")
        raise

def main():
    """Main function to create assets table and sample data"""
    try:
        logger.info("🚀 Starting assets initialization...")
        
        # Create engine
        engine = create_database_engine()
        
        # Create assets table
        create_assets_table(engine)
        
        # Create sample assets
        create_sample_assets(engine)
        
        # Verify assets
        verify_assets(engine)
        
        logger.info("🎉 Assets initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Assets initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 