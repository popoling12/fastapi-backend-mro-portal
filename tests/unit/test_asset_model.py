import pytest
from datetime import datetime
from app.models.asset import Asset, AssetType, AssetStatus


def test_asset_creation():
    """Test basic asset creation"""
    asset = Asset(
        name="Test Plant",
        code="TEST001",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE,
        location="Test Location",
        installation_date=datetime.now(),
        manufacturer="Test Manufacturer",
        model_number="TEST-MODEL-001",
        config={"capacity_mw": 100}
    )
    
    assert asset.name == "Test Plant"
    assert asset.code == "TEST001"
    assert asset.asset_type == AssetType.PLANT
    assert asset.status == AssetStatus.ACTIVE
    assert asset.location == "Test Location"
    assert asset.manufacturer == "Test Manufacturer"
    assert asset.model_number == "TEST-MODEL-001"
    assert asset.config == {"capacity_mw": 100}
    assert asset.uuid is not None  # UUID should be auto-generated


def test_asset_hierarchy():
    """Test asset parent-child relationships"""
    parent = Asset(
        name="Parent Plant",
        code="PARENT001",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE
    )
    
    child = Asset(
        name="Child Sub-plant",
        code="CHILD001",
        asset_type=AssetType.SUB_PLANT,
        status=AssetStatus.ACTIVE,
        parent=parent
    )
    
    assert child.parent == parent
    assert parent in child.parent.children


def test_asset_status_transition():
    """Test asset status transitions"""
    asset = Asset(
        name="Test Asset",
        code="TEST002",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE
    )
    
    # Test valid status transitions
    asset.status = AssetStatus.MAINTENANCE
    assert asset.status == AssetStatus.MAINTENANCE
    
    asset.status = AssetStatus.INACTIVE
    assert asset.status == AssetStatus.INACTIVE
    
    asset.status = AssetStatus.DECOMMISSIONED
    assert asset.status == AssetStatus.DECOMMISSIONED


def test_asset_config():
    """Test asset configuration handling"""
    # Test plant config
    plant = Asset(
        name="Test Plant",
        code="TEST003",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE,
        config={
            "capacity_mw": 100,
            "total_panels": 250000,
            "total_inverters": 1000
        }
    )
    assert plant.config["capacity_mw"] == 100
    assert plant.config["total_panels"] == 250000
    
    # Test inverter config
    inverter = Asset(
        name="Test Inverter",
        code="TEST004",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE,
        config={
            "capacity_kw": 1000,
            "efficiency": 0.98,
            "max_voltage": 1000
        }
    )
    assert inverter.config["capacity_kw"] == 1000
    assert inverter.config["efficiency"] == 0.98


def test_asset_realtime_data():
    """Test asset realtime data tag handling"""
    asset = Asset(
        name="Test Asset",
        code="TEST005",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE,
        realtime_data_tag="PLT001/SUB001/INV001"
    )
    
    assert asset.realtime_data_tag == "PLT001/SUB001/INV001"


def test_asset_audit_fields():
    """Test asset audit fields"""
    asset = Asset(
        name="Test Asset",
        code="TEST006",
        asset_type=AssetType.SENSOR,
        status=AssetStatus.ACTIVE
    )
    
    assert asset.created_at is not None
    assert asset.updated_at is not None
    assert asset.created_by_id is None  # Should be set when created by a user 