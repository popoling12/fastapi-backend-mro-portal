import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.asset import Asset, AssetType, AssetStatus
from app.crud import crud_asset
from app.schemas.asset import AssetCreate, AssetUpdate


def test_create_asset(db: Session):
    """Test creating a new asset"""
    asset_in = AssetCreate(
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
    
    asset = crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    assert asset.name == asset_in.name
    assert asset.code == asset_in.code
    assert asset.asset_type == asset_in.asset_type
    assert asset.status == asset_in.status
    assert asset.location == asset_in.location
    assert asset.manufacturer == asset_in.manufacturer
    assert asset.model_number == asset_in.model_number
    assert asset.config == asset_in.config
    assert asset.created_by_id == 1


def test_get_asset(db: Session):
    """Test retrieving an asset by ID"""
    # Create test asset
    asset_in = AssetCreate(
        name="Test Asset",
        code="TEST002",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE
    )
    created_asset = crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    # Retrieve asset
    retrieved_asset = crud_asset.get_asset(db=db, asset_id=created_asset.id)
    
    assert retrieved_asset is not None
    assert retrieved_asset.id == created_asset.id
    assert retrieved_asset.name == created_asset.name
    assert retrieved_asset.code == created_asset.code


def test_get_asset_by_code(db: Session):
    """Test retrieving an asset by code"""
    # Create test asset
    asset_in = AssetCreate(
        name="Test Asset",
        code="TEST003",
        asset_type=AssetType.STRING,
        status=AssetStatus.ACTIVE
    )
    created_asset = crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    # Retrieve asset
    retrieved_asset = crud_asset.get_asset_by_code(db=db, code=created_asset.code)
    
    assert retrieved_asset is not None
    assert retrieved_asset.id == created_asset.id
    assert retrieved_asset.code == created_asset.code


def test_get_assets(db: Session):
    """Test retrieving multiple assets with filters"""
    # Create test assets
    assets = [
        AssetCreate(
            name=f"Test Asset {i}",
            code=f"TEST{i:03d}",
            asset_type=AssetType.INVERTER,
            status=AssetStatus.ACTIVE
        )
        for i in range(5)
    ]
    
    for asset_in in assets:
        crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    # Test getting all assets
    all_assets = crud_asset.get_assets(db=db)
    assert len(all_assets) >= 5
    
    # Test filtering by asset type
    inverter_assets = crud_asset.get_assets(db=db, asset_type=AssetType.INVERTER)
    assert all(asset.asset_type == AssetType.INVERTER for asset in inverter_assets)
    
    # Test filtering by status
    active_assets = crud_asset.get_assets(db=db, status=AssetStatus.ACTIVE)
    assert all(asset.status == AssetStatus.ACTIVE for asset in active_assets)


def test_update_asset(db: Session):
    """Test updating an asset"""
    # Create test asset
    asset_in = AssetCreate(
        name="Test Asset",
        code="TEST004",
        asset_type=AssetType.PANEL,
        status=AssetStatus.ACTIVE
    )
    created_asset = crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    # Update asset
    update_data = AssetUpdate(
        name="Updated Asset",
        status=AssetStatus.MAINTENANCE,
        config={"capacity_w": 400}
    )
    updated_asset = crud_asset.update_asset(
        db=db,
        db_asset=created_asset,
        asset_update=update_data
    )
    
    assert updated_asset.name == "Updated Asset"
    assert updated_asset.status == AssetStatus.MAINTENANCE
    assert updated_asset.config == {"capacity_w": 400}
    assert updated_asset.code == created_asset.code  # Unchanged fields should remain


def test_delete_asset(db: Session):
    """Test deleting an asset"""
    # Create test asset
    asset_in = AssetCreate(
        name="Test Asset",
        code="TEST005",
        asset_type=AssetType.SENSOR,
        status=AssetStatus.ACTIVE
    )
    created_asset = crud_asset.create_asset(db=db, asset=asset_in, created_by_id=1)
    
    # Delete asset
    result = crud_asset.delete_asset(db=db, asset_id=created_asset.id)
    assert result is True
    
    # Verify asset is deleted
    deleted_asset = crud_asset.get_asset(db=db, asset_id=created_asset.id)
    assert deleted_asset is None


def test_get_asset_hierarchy(db: Session):
    """Test retrieving asset hierarchy"""
    # Create parent asset
    parent_in = AssetCreate(
        name="Parent Plant",
        code="PARENT001",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE
    )
    parent = crud_asset.create_asset(db=db, asset=parent_in, created_by_id=1)
    
    # Create child assets
    child_in = AssetCreate(
        name="Child Sub-plant",
        code="CHILD001",
        asset_type=AssetType.SUB_PLANT,
        status=AssetStatus.ACTIVE,
        parent_id=parent.id
    )
    child = crud_asset.create_asset(db=db, asset=child_in, created_by_id=1)
    
    # Get hierarchy
    hierarchy = crud_asset.get_asset_hierarchy(db=db, asset_id=parent.id)
    
    assert len(hierarchy) == 2
    assert parent in hierarchy
    assert child in hierarchy


def test_get_asset_ancestors(db: Session):
    """Test retrieving asset ancestors"""
    # Create grandparent asset
    grandparent_in = AssetCreate(
        name="Grandparent Plant",
        code="GRAND001",
        asset_type=AssetType.PLANT,
        status=AssetStatus.ACTIVE
    )
    grandparent = crud_asset.create_asset(db=db, asset=grandparent_in, created_by_id=1)
    
    # Create parent asset
    parent_in = AssetCreate(
        name="Parent Sub-plant",
        code="PARENT002",
        asset_type=AssetType.SUB_PLANT,
        status=AssetStatus.ACTIVE,
        parent_id=grandparent.id
    )
    parent = crud_asset.create_asset(db=db, asset=parent_in, created_by_id=1)
    
    # Create child asset
    child_in = AssetCreate(
        name="Child Inverter",
        code="CHILD002",
        asset_type=AssetType.INVERTER,
        status=AssetStatus.ACTIVE,
        parent_id=parent.id
    )
    child = crud_asset.create_asset(db=db, asset=child_in, created_by_id=1)
    
    # Get ancestors
    ancestors = crud_asset.get_asset_ancestors(db=db, asset_id=child.id)
    
    assert len(ancestors) == 2
    assert parent in ancestors
    assert grandparent in ancestors 