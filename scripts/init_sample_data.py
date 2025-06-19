#!/usr/bin/env python3
"""
Script to initialize sample data for the new asset model structure.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.asset import (
    Location, AssetTemplate, StoreInventory, Asset, AssetItem, AssetSensor,
    AssetType, AssetStatus, TemplateCategory
)
from app.models.user import User
from app.crud import crud_user


def create_sample_locations(db: Session):
    """Create sample locations"""
    print("Creating sample locations...")
    
    # Root location
    root_location = Location(
        name="Solar Plant Complex",
        code="SPC-001",
        description="Main solar plant complex"
    )
    db.add(root_location)
    db.flush()
    
    # Sub-locations
    locations = [
        Location(
            name="Plant A",
            code="PLANT-A",
            description="Solar Plant A",
            parent_id=root_location.id
        ),
        Location(
            name="Plant B", 
            code="PLANT-B",
            description="Solar Plant B",
            parent_id=root_location.id
        ),
        Location(
            name="Inverter Station 1",
            code="INV-001",
            description="Inverter station for Plant A",
            parent_id=root_location.id
        ),
        Location(
            name="String Array 1",
            code="STR-001", 
            description="String array 1 in Plant A",
            parent_id=root_location.id
        )
    ]
    
    for location in locations:
        db.add(location)
    
    db.commit()
    print(f"Created {len(locations) + 1} sample locations")
    return root_location


def create_sample_templates(db: Session):
    """Create sample asset templates"""
    print("Creating sample asset templates...")
    
    templates = [
        # Hardware templates
        AssetTemplate(
            name="Solar Panel 400W",
            code="PANEL-400W",
            asset_type=AssetType.PANEL,
            category=TemplateCategory.HARDWARE,
            manufacturer="SolarTech",
            model_number="ST-400W-M",
            description="400W monocrystalline solar panel",
            default_config={"wattage": 400, "voltage": 24, "efficiency": 0.21},
            unit_price=150.00
        ),
        AssetTemplate(
            name="String Inverter 5kW",
            code="INV-5KW",
            asset_type=AssetType.INVERTER,
            category=TemplateCategory.HARDWARE,
            manufacturer="PowerFlow",
            model_number="PF-5KW-S",
            description="5kW string inverter",
            default_config={"power_rating": 5000, "efficiency": 0.96, "input_voltage": "600V"},
            unit_price=800.00
        ),
        AssetTemplate(
            name="Solar Plant Controller",
            code="CTRL-PLANT",
            asset_type=AssetType.PLANT,
            category=TemplateCategory.HARDWARE,
            manufacturer="PlantControl",
            model_number="PC-1000",
            description="Plant level controller",
            default_config={"max_plants": 10, "communication": "Modbus TCP"},
            unit_price=2500.00
        ),
        
        # Consumable templates
        AssetTemplate(
            name="Cleaning Solution",
            code="CLEAN-SOL",
            asset_type=AssetType.SENSOR,
            category=TemplateCategory.CONSUMABLE,
            manufacturer="CleanTech",
            model_number="CS-500ML",
            description="Solar panel cleaning solution",
            unit_price=25.00
        ),
        
        # License templates
        AssetTemplate(
            name="Monitoring Software License",
            code="LIC-MONITOR",
            asset_type=AssetType.SENSOR,
            category=TemplateCategory.LICENSE,
            manufacturer="MonitorSoft",
            model_number="MS-PRO-1YR",
            description="Professional monitoring software license",
            unit_price=500.00,
            license_duration_days=365
        )
    ]
    
    for template in templates:
        db.add(template)
    
    db.commit()
    print(f"Created {len(templates)} sample templates")
    return templates


def create_sample_inventory(db: Session, templates):
    """Create sample store inventory"""
    print("Creating sample store inventory...")
    
    inventory_items = [
        StoreInventory(
            template_id=templates[0].id,  # Solar Panel
            quantity=100,
            storage_location="Warehouse A - Section 1"
        ),
        StoreInventory(
            template_id=templates[1].id,  # Inverter
            quantity=20,
            storage_location="Warehouse A - Section 2"
        ),
        StoreInventory(
            template_id=templates[2].id,  # Controller
            quantity=5,
            storage_location="Warehouse B - Section 1"
        ),
        StoreInventory(
            template_id=templates[3].id,  # Cleaning Solution
            quantity=50,
            storage_location="Warehouse C - Section 1"
        ),
        StoreInventory(
            template_id=templates[4].id,  # License
            quantity=10,
            storage_location="Digital - License Server"
        )
    ]
    
    for item in inventory_items:
        db.add(item)
    
    db.commit()
    print(f"Created {len(inventory_items)} inventory items")


def create_sample_assets(db: Session, location, templates):
    """Create sample assets"""
    print("Creating sample assets...")
    
    # Create a plant
    plant = Asset(
        name="Solar Plant Alpha",
        code="PLANT-ALPHA-001",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE,
        location_id=location.id,
        template_id=templates[2].id,  # Controller template
        installation_date=datetime.now() - timedelta(days=30),
        config={"capacity_mw": 5.0, "grid_connection": "10kV"},
        realtime_data_tag="plant.alpha.001"
    )
    db.add(plant)
    db.flush()
    
    # Create an inverter
    inverter = Asset(
        name="Inverter Station 1",
        code="INV-001",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE,
        parent_id=plant.id,
        location_id=location.id,
        template_id=templates[1].id,  # Inverter template
        installation_date=datetime.now() - timedelta(days=25),
        config={"power_rating": 5000, "efficiency": 0.96},
        realtime_data_tag="inverter.001"
    )
    db.add(inverter)
    db.flush()
    
    # Create a string
    string = Asset(
        name="String Array 1",
        code="STR-001",
        asset_type=AssetType.STRING,
        status=AssetStatus.ACTIVE,
        parent_id=inverter.id,
        location_id=location.id,
        installation_date=datetime.now() - timedelta(days=20),
        config={"panel_count": 20, "voltage": 600},
        realtime_data_tag="string.001"
    )
    db.add(string)
    db.flush()
    
    # Create panels
    panels = []
    for i in range(1, 21):
        panel = Asset(
            name=f"Panel {i:03d}",
            code=f"PANEL-{i:03d}",
            asset_type=AssetType.PANEL,
            status=AssetStatus.ACTIVE,
            parent_id=string.id,
            location_id=location.id,
            template_id=templates[0].id,  # Panel template
            installation_date=datetime.now() - timedelta(days=15),
            config={"position": i, "wattage": 400},
            realtime_data_tag=f"panel.{i:03d}"
        )
        panels.append(panel)
        db.add(panel)
    
    db.commit()
    print(f"Created 1 plant, 1 inverter, 1 string, and {len(panels)} panels")
    return plant, inverter, string, panels


def create_sample_items(db: Session, assets, templates):
    """Create sample asset items (consumables/licenses)"""
    print("Creating sample asset items...")
    
    plant, inverter, string, panels = assets
    
    items = [
        # Cleaning solution for the plant
        AssetItem(
            asset_id=plant.id,
            template_id=templates[3].id,  # Cleaning solution
            quantity=5
        ),
        # License for the plant
        AssetItem(
            asset_id=plant.id,
            template_id=templates[4].id,  # License
            quantity=1,
            expires_at=datetime.now() + timedelta(days=335)  # 1 year - 30 days
        )
    ]
    
    for item in items:
        db.add(item)
    
    db.commit()
    print(f"Created {len(items)} asset items")


def create_sample_sensors(db: Session, assets):
    """Create sample asset sensors"""
    print("Creating sample asset sensors...")
    
    plant, inverter, string, panels = assets
    
    sensors = [
        # Plant sensors
        AssetSensor(
            asset_id=plant.id,
            name="Power Output",
            sensor_path="plant.alpha.001.power",
            system_source="SCADA",
            config={"unit": "kW", "update_interval": 5}
        ),
        AssetSensor(
            asset_id=plant.id,
            name="Temperature",
            sensor_path="plant.alpha.001.temp",
            system_source="SCADA",
            config={"unit": "°C", "update_interval": 10}
        ),
        
        # Inverter sensors
        AssetSensor(
            asset_id=inverter.id,
            name="AC Power Output",
            sensor_path="inverter.001.ac_power",
            system_source="Inverter Controller",
            config={"unit": "kW", "update_interval": 1}
        ),
        AssetSensor(
            asset_id=inverter.id,
            name="DC Input Voltage",
            sensor_path="inverter.001.dc_voltage",
            system_source="Inverter Controller",
            config={"unit": "V", "update_interval": 1}
        ),
        
        # String sensors
        AssetSensor(
            asset_id=string.id,
            name="String Current",
            sensor_path="string.001.current",
            system_source="String Monitor",
            config={"unit": "A", "update_interval": 5}
        ),
        AssetSensor(
            asset_id=string.id,
            name="String Voltage",
            sensor_path="string.001.voltage",
            system_source="String Monitor",
            config={"unit": "V", "update_interval": 5}
        ),
        
        # Panel sensors (just a few examples)
        AssetSensor(
            asset_id=panels[0].id,
            name="Panel Temperature",
            sensor_path="panel.001.temp",
            system_source="Panel Monitor",
            config={"unit": "°C", "update_interval": 30}
        ),
        AssetSensor(
            asset_id=panels[0].id,
            name="Panel Voltage",
            sensor_path="panel.001.voltage",
            system_source="Panel Monitor",
            config={"unit": "V", "update_interval": 30}
        )
    ]
    
    for sensor in sensors:
        db.add(sensor)
    
    db.commit()
    print(f"Created {len(sensors)} asset sensors")


def main():
    """Main function to create sample data"""
    print("=" * 60)
    print("SAMPLE DATA INITIALIZATION")
    print("=" * 60)
    
    try:
        # Create database session
        db = Session(engine)
        
        # Create sample data
        location = create_sample_locations(db)
        templates = create_sample_templates(db)
        create_sample_inventory(db, templates)
        assets = create_sample_assets(db, location, templates)
        create_sample_items(db, assets, templates)
        create_sample_sensors(db, assets)
        
        print("=" * 60)
        print("Sample data initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during sample data initialization: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main() 