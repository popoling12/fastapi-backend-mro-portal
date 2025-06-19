from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.asset import (
    Asset, AssetType, AssetStatus, Location, AssetTemplate, 
    StoreInventory, AssetItem, AssetSensor, TemplateCategory
)
from app.schemas.asset import (
    AssetCreate, AssetUpdate, LocationCreate, LocationUpdate,
    AssetTemplateCreate, AssetTemplateUpdate, StoreInventoryCreate, 
    StoreInventoryUpdate, AssetItemCreate, AssetItemUpdate,
    AssetSensorCreate, AssetSensorUpdate
)


# Location CRUD operations
def get_location(db: Session, location_id: int) -> Optional[Location]:
    """Get a single location by ID"""
    return db.query(Location).filter(Location.id == location_id).first()


def get_location_by_uuid(db: Session, uuid: str) -> Optional[Location]:
    """Get a single location by UUID"""
    return db.query(Location).filter(Location.uuid == uuid).first()


def get_location_by_code(db: Session, code: str) -> Optional[Location]:
    """Get a single location by code"""
    return db.query(Location).filter(Location.code == code).first()


def get_locations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None
) -> List[Location]:
    """Get multiple locations with optional filters"""
    query = db.query(Location)
    
    if parent_id is not None:
        query = query.filter(Location.parent_id == parent_id)
    
    return query.offset(skip).limit(limit).all()


def create_location(db: Session, location: LocationCreate) -> Location:
    """Create a new location"""
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(
    db: Session,
    db_location: Location,
    location_update: LocationUpdate
) -> Location:
    """Update an existing location"""
    update_data = location_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int) -> bool:
    """Delete a location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if location:
        db.delete(location)
        db.commit()
        return True
    return False


# AssetTemplate CRUD operations
def get_asset_template(db: Session, template_id: int) -> Optional[AssetTemplate]:
    """Get a single asset template by ID"""
    return db.query(AssetTemplate).filter(AssetTemplate.id == template_id).first()


def get_asset_template_by_uuid(db: Session, uuid: str) -> Optional[AssetTemplate]:
    """Get a single asset template by UUID"""
    return db.query(AssetTemplate).filter(AssetTemplate.uuid == uuid).first()


def get_asset_template_by_code(db: Session, code: str) -> Optional[AssetTemplate]:
    """Get a single asset template by code"""
    return db.query(AssetTemplate).filter(AssetTemplate.code == code).first()


def get_asset_templates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[AssetType] = None,
    category: Optional[TemplateCategory] = None
) -> List[AssetTemplate]:
    """Get multiple asset templates with optional filters"""
    query = db.query(AssetTemplate)
    
    if asset_type:
        query = query.filter(AssetTemplate.asset_type == asset_type)
    if category:
        query = query.filter(AssetTemplate.category == category)
    
    return query.offset(skip).limit(limit).all()


def create_asset_template(db: Session, template: AssetTemplateCreate) -> AssetTemplate:
    """Create a new asset template"""
    db_template = AssetTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_asset_template(
    db: Session,
    db_template: AssetTemplate,
    template_update: AssetTemplateUpdate
) -> AssetTemplate:
    """Update an existing asset template"""
    update_data = template_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def delete_asset_template(db: Session, template_id: int) -> bool:
    """Delete an asset template"""
    template = db.query(AssetTemplate).filter(AssetTemplate.id == template_id).first()
    if template:
        db.delete(template)
        db.commit()
        return True
    return False


# StoreInventory CRUD operations
def get_store_inventory(db: Session, inventory_id: int) -> Optional[StoreInventory]:
    """Get a single store inventory by ID"""
    return db.query(StoreInventory).filter(StoreInventory.id == inventory_id).first()


def get_store_inventory_by_template(db: Session, template_id: int) -> Optional[StoreInventory]:
    """Get store inventory by template ID"""
    return db.query(StoreInventory).filter(StoreInventory.template_id == template_id).first()


def get_store_inventories(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[StoreInventory]:
    """Get multiple store inventories"""
    return db.query(StoreInventory).offset(skip).limit(limit).all()


def create_store_inventory(db: Session, inventory: StoreInventoryCreate) -> StoreInventory:
    """Create a new store inventory"""
    db_inventory = StoreInventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_store_inventory(
    db: Session,
    db_inventory: StoreInventory,
    inventory_update: StoreInventoryUpdate
) -> StoreInventory:
    """Update an existing store inventory"""
    update_data = inventory_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_inventory, field, value)
    
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def delete_store_inventory(db: Session, inventory_id: int) -> bool:
    """Delete a store inventory"""
    inventory = db.query(StoreInventory).filter(StoreInventory.id == inventory_id).first()
    if inventory:
        db.delete(inventory)
        db.commit()
        return True
    return False


# Asset CRUD operations
def get_asset(db: Session, asset_id: int) -> Optional[Asset]:
    """Get a single asset by ID"""
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_asset_by_uuid(db: Session, uuid: str) -> Optional[Asset]:
    """Get a single asset by UUID"""
    return db.query(Asset).filter(Asset.uuid == uuid).first()


def get_asset_by_code(db: Session, code: str) -> Optional[Asset]:
    """Get a single asset by code"""
    return db.query(Asset).filter(Asset.code == code).first()


def get_assets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    parent_id: Optional[int] = None,
    location_id: Optional[int] = None
) -> List[Asset]:
    """Get multiple assets with optional filters"""
    query = db.query(Asset)
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    if parent_id is not None:
        query = query.filter(Asset.parent_id == parent_id)
    if location_id is not None:
        query = query.filter(Asset.location_id == location_id)
    
    return query.offset(skip).limit(limit).all()


def create_asset(db: Session, asset: AssetCreate, created_by_id: int) -> Asset:
    """Create a new asset"""
    db_asset = Asset(**asset.dict(), created_by_id=created_by_id)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def update_asset(
    db: Session,
    db_asset: Asset,
    asset_update: AssetUpdate
) -> Asset:
    """Update an existing asset"""
    update_data = asset_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_asset, field, value)
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def delete_asset(db: Session, asset_id: int) -> bool:
    """Delete an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset:
        db.delete(asset)
        db.commit()
        return True
    return False


def get_asset_hierarchy(db: Session, asset_id: int) -> List[Asset]:
    """Get the complete hierarchy of an asset (all children)"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return []
    
    hierarchy = [asset]
    children = db.query(Asset).filter(Asset.parent_id == asset_id).all()
    
    for child in children:
        hierarchy.extend(get_asset_hierarchy(db, child.id))
    
    return hierarchy


def get_asset_ancestors(db: Session, asset_id: int) -> List[Asset]:
    """Get all ancestors of an asset (parent chain)"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return []
    
    ancestors = []
    current = asset
    
    while current.parent_id:
        parent = db.query(Asset).filter(Asset.id == current.parent_id).first()
        if parent:
            ancestors.append(parent)
            current = parent
        else:
            break
    
    return ancestors


# AssetItem CRUD operations
def get_asset_item(db: Session, item_id: int) -> Optional[AssetItem]:
    """Get a single asset item by ID"""
    return db.query(AssetItem).filter(AssetItem.id == item_id).first()


def get_asset_items_by_asset(db: Session, asset_id: int) -> List[AssetItem]:
    """Get all items for a specific asset"""
    return db.query(AssetItem).filter(AssetItem.asset_id == asset_id).all()


def get_asset_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    template_id: Optional[int] = None
) -> List[AssetItem]:
    """Get multiple asset items with optional filters"""
    query = db.query(AssetItem)
    
    if asset_id:
        query = query.filter(AssetItem.asset_id == asset_id)
    if template_id:
        query = query.filter(AssetItem.template_id == template_id)
    
    return query.offset(skip).limit(limit).all()


def create_asset_item(db: Session, item: AssetItemCreate) -> AssetItem:
    """Create a new asset item"""
    db_item = AssetItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_asset_item(
    db: Session,
    db_item: AssetItem,
    item_update: AssetItemUpdate
) -> AssetItem:
    """Update an existing asset item"""
    update_data = item_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_asset_item(db: Session, item_id: int) -> bool:
    """Delete an asset item"""
    item = db.query(AssetItem).filter(AssetItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False


# AssetSensor CRUD operations
def get_asset_sensor(db: Session, sensor_id: int) -> Optional[AssetSensor]:
    """Get a single asset sensor by ID"""
    return db.query(AssetSensor).filter(AssetSensor.id == sensor_id).first()


def get_asset_sensor_by_uuid(db: Session, uuid: str) -> Optional[AssetSensor]:
    """Get a single asset sensor by UUID"""
    return db.query(AssetSensor).filter(AssetSensor.uuid == uuid).first()


def get_asset_sensors_by_asset(db: Session, asset_id: int) -> List[AssetSensor]:
    """Get all sensors for a specific asset"""
    return db.query(AssetSensor).filter(AssetSensor.asset_id == asset_id).all()


def get_asset_sensors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    system_source: Optional[str] = None
) -> List[AssetSensor]:
    """Get multiple asset sensors with optional filters"""
    query = db.query(AssetSensor)
    
    if asset_id:
        query = query.filter(AssetSensor.asset_id == asset_id)
    if system_source:
        query = query.filter(AssetSensor.system_source == system_source)
    
    return query.offset(skip).limit(limit).all()


def create_asset_sensor(db: Session, sensor: AssetSensorCreate) -> AssetSensor:
    """Create a new asset sensor"""
    db_sensor = AssetSensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


def update_asset_sensor(
    db: Session,
    db_sensor: AssetSensor,
    sensor_update: AssetSensorUpdate
) -> AssetSensor:
    """Update an existing asset sensor"""
    update_data = sensor_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_sensor, field, value)
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


def delete_asset_sensor(db: Session, sensor_id: int) -> bool:
    """Delete an asset sensor"""
    sensor = db.query(AssetSensor).filter(AssetSensor.id == sensor_id).first()
    if sensor:
        db.delete(sensor)
        db.commit()
        return True
    return False 