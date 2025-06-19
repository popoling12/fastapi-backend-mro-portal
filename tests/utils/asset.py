import random
import string
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetType, AssetStatus
from app.crud import crud_asset
from app.schemas.asset import AssetCreate


def random_lower_string() -> str:
    """Generate a random string"""
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_asset_code(asset_type: AssetType) -> str:
    """Generate a random asset code based on type"""
    prefix = {
        AssetType.PLANT: "PLT",
        AssetType.SUB_PLANT: "SUB",
        AssetType.INVERTER: "INV",
        AssetType.STRING: "STR",
        AssetType.PANEL: "PAN",
        AssetType.SENSOR: "SEN"
    }.get(asset_type, "AST")
    
    return f"{prefix}{random.randint(100, 999)}"


def create_random_asset(
    db: Session,
    *,
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    parent_id: Optional[int] = None
) -> Asset:
    """Create a random asset for testing"""
    if asset_type is None:
        asset_type = random.choice(list(AssetType))
    
    if status is None:
        status = random.choice(list(AssetStatus))
    
    # Generate appropriate config based on asset type
    config = {
        AssetType.PLANT: {
            "capacity_mw": random.randint(50, 500),
            "total_panels": random.randint(100000, 1000000),
            "total_inverters": random.randint(100, 1000)
        },
        AssetType.SUB_PLANT: {
            "capacity_mw": random.randint(10, 100),
            "total_panels": random.randint(10000, 100000),
            "total_inverters": random.randint(10, 100)
        },
        AssetType.INVERTER: {
            "capacity_kw": random.randint(100, 1000),
            "efficiency": round(random.uniform(0.95, 0.99), 2),
            "max_voltage": random.randint(800, 1200),
            "max_current": random.randint(50, 150)
        },
        AssetType.STRING: {
            "panel_count": random.randint(10, 30),
            "max_voltage": random.randint(800, 1200),
            "max_current": random.randint(5, 15)
        },
        AssetType.PANEL: {
            "capacity_w": random.randint(300, 500),
            "efficiency": round(random.uniform(0.18, 0.22), 2),
            "max_voltage": random.randint(30, 50),
            "max_current": random.randint(8, 12)
        },
        AssetType.SENSOR: {
            "sensor_types": random.sample(
                ["temperature", "humidity", "wind_speed", "irradiance", "pressure"],
                k=random.randint(1, 5)
            ),
            "update_interval": random.randint(30, 300),
            "battery_life": random.randint(180, 365)
        }
    }.get(asset_type, {})
    
    # Generate realtime data tag if applicable
    realtime_data_tag = None
    if asset_type in [AssetType.INVERTER, AssetType.STRING, AssetType.SENSOR]:
        realtime_data_tag = f"PLT001/SUB001/{asset_type.value.upper()}{random.randint(1, 999):03d}"
    
    asset_in = AssetCreate(
        name=f"Test {asset_type.value.title()} {random.randint(1, 1000)}",
        code=random_asset_code(asset_type),
        asset_type=asset_type,
        status=status,
        location=f"Test Location {random.randint(1, 100)}",
        installation_date=datetime.now(),
        manufacturer=f"Test Manufacturer {random.randint(1, 10)}",
        model_number=f"TEST-{asset_type.value.upper()}-{random.randint(100, 999)}",
        serial_number=f"SN{random.randint(100000, 999999)}",
        config=config,
        realtime_data_tag=realtime_data_tag,
        parent_id=parent_id
    )
    
    return crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1) 