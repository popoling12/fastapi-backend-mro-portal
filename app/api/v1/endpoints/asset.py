from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_asset
from app.models.asset import AssetType, AssetStatus, TemplateCategory
from app.schemas.asset import (
    Asset,
    AssetCreate,
    AssetUpdate,
    AssetHierarchy,
    AssetAncestors,
    Location,
    LocationCreate,
    LocationUpdate,
    AssetTemplate,
    AssetTemplateCreate,
    AssetTemplateUpdate,
    StoreInventory,
    StoreInventoryCreate,
    StoreInventoryUpdate,
    AssetItem,
    AssetItemCreate,
    AssetItemUpdate,
    AssetSensor,
    AssetSensorCreate,
    AssetSensorUpdate
)
from app.models.user import User

router = APIRouter()


# Location endpoints
@router.get("/locations/", response_model=List[Location])
def read_locations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[Location]:
    """
    Retrieve locations with optional filtering.
    """
    locations = crud_asset.get_locations(
        db=db,
        skip=skip,
        limit=limit,
        parent_id=parent_id
    )
    return locations


@router.post("/locations/", response_model=Location)
def create_location(
    *,
    db: Session = Depends(deps.get_db),
    location_in: LocationCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Location:
    """
    Create new location.
    """
    # Check if location with same code exists
    if location_in.code:
        location = crud_asset.get_location_by_code(db, code=location_in.code)
        if location:
            raise HTTPException(
                status_code=400,
                detail="A location with this code already exists."
            )
    
    # If parent_id is provided, verify parent exists
    if location_in.parent_id:
        parent = crud_asset.get_location(db, location_id=location_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent location not found."
            )
    
    location = crud_asset.create_location(db=db, location=location_in)
    return location


@router.get("/locations/{location_id}", response_model=Location)
def read_location(
    *,
    db: Session = Depends(deps.get_db),
    location_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Location:
    """
    Get location by ID.
    """
    location = crud_asset.get_location(db, location_id=location_id)
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )
    return location


@router.put("/locations/{location_id}", response_model=Location)
def update_location(
    *,
    db: Session = Depends(deps.get_db),
    location_id: int,
    location_in: LocationUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Location:
    """
    Update a location.
    """
    location = crud_asset.get_location(db, location_id=location_id)
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )
    
    # If code is being updated, check for duplicates
    if location_in.code and location_in.code != location.code:
        existing_location = crud_asset.get_location_by_code(db, code=location_in.code)
        if existing_location:
            raise HTTPException(
                status_code=400,
                detail="A location with this code already exists."
            )
    
    # If parent_id is being updated, verify new parent exists
    if location_in.parent_id and location_in.parent_id != location.parent_id:
        parent = crud_asset.get_location(db, location_id=location_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent location not found."
            )
    
    location = crud_asset.update_location(
        db=db,
        db_location=location,
        location_update=location_in
    )
    return location


@router.delete("/locations/{location_id}", response_model=bool)
def delete_location(
    *,
    db: Session = Depends(deps.get_db),
    location_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete a location.
    """
    location = crud_asset.get_location(db, location_id=location_id)
    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )
    
    # Check if location has children
    children = crud_asset.get_locations(db, parent_id=location_id)
    if children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete location with children. Please delete or reassign children first."
        )
    
    return crud_asset.delete_location(db=db, location_id=location_id)


# AssetTemplate endpoints
@router.get("/templates/", response_model=List[AssetTemplate])
def read_asset_templates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[AssetType] = None,
    category: Optional[TemplateCategory] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[AssetTemplate]:
    """
    Retrieve asset templates with optional filtering.
    """
    templates = crud_asset.get_asset_templates(
        db=db,
        skip=skip,
        limit=limit,
        asset_type=asset_type,
        category=category
    )
    return templates


@router.post("/templates/", response_model=AssetTemplate)
def create_asset_template(
    *,
    db: Session = Depends(deps.get_db),
    template_in: AssetTemplateCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetTemplate:
    """
    Create new asset template.
    """
    # Check if template with same code exists
    if template_in.code:
        template = crud_asset.get_asset_template_by_code(db, code=template_in.code)
        if template:
            raise HTTPException(
                status_code=400,
                detail="An asset template with this code already exists."
            )
    
    template = crud_asset.create_asset_template(db=db, template=template_in)
    return template


@router.get("/templates/{template_id}", response_model=AssetTemplate)
def read_asset_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetTemplate:
    """
    Get asset template by ID.
    """
    template = crud_asset.get_asset_template(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Asset template not found"
        )
    return template


@router.put("/templates/{template_id}", response_model=AssetTemplate)
def update_asset_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    template_in: AssetTemplateUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetTemplate:
    """
    Update an asset template.
    """
    template = crud_asset.get_asset_template(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Asset template not found"
        )
    
    # If code is being updated, check for duplicates
    if template_in.code and template_in.code != template.code:
        existing_template = crud_asset.get_asset_template_by_code(db, code=template_in.code)
        if existing_template:
            raise HTTPException(
                status_code=400,
                detail="An asset template with this code already exists."
            )
    
    template = crud_asset.update_asset_template(
        db=db,
        db_template=template,
        template_update=template_in
    )
    return template


@router.delete("/templates/{template_id}", response_model=bool)
def delete_asset_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete an asset template.
    """
    template = crud_asset.get_asset_template(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Asset template not found"
        )
    
    return crud_asset.delete_asset_template(db=db, template_id=template_id)


# StoreInventory endpoints
@router.get("/inventory/", response_model=List[StoreInventory])
def read_store_inventories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[StoreInventory]:
    """
    Retrieve store inventories.
    """
    inventories = crud_asset.get_store_inventories(
        db=db,
        skip=skip,
        limit=limit
    )
    return inventories


@router.post("/inventory/", response_model=StoreInventory)
def create_store_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_in: StoreInventoryCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> StoreInventory:
    """
    Create new store inventory.
    """
    # Check if template exists
    template = crud_asset.get_asset_template(db, template_id=inventory_in.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Asset template not found"
        )
    
    # Check if inventory already exists for this template
    existing_inventory = crud_asset.get_store_inventory_by_template(
        db, template_id=inventory_in.template_id
    )
    if existing_inventory:
        raise HTTPException(
            status_code=400,
            detail="Inventory already exists for this template. Use update instead."
        )
    
    inventory = crud_asset.create_store_inventory(db=db, inventory=inventory_in)
    return inventory


@router.get("/inventory/{inventory_id}", response_model=StoreInventory)
def read_store_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> StoreInventory:
    """
    Get store inventory by ID.
    """
    inventory = crud_asset.get_store_inventory(db, inventory_id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Store inventory not found"
        )
    return inventory


@router.put("/inventory/{inventory_id}", response_model=StoreInventory)
def update_store_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_id: int,
    inventory_in: StoreInventoryUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> StoreInventory:
    """
    Update a store inventory.
    """
    inventory = crud_asset.get_store_inventory(db, inventory_id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Store inventory not found"
        )
    
    inventory = crud_asset.update_store_inventory(
        db=db,
        db_inventory=inventory,
        inventory_update=inventory_in
    )
    return inventory


@router.delete("/inventory/{inventory_id}", response_model=bool)
def delete_store_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete a store inventory.
    """
    inventory = crud_asset.get_store_inventory(db, inventory_id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Store inventory not found"
        )
    
    return crud_asset.delete_store_inventory(db=db, inventory_id=inventory_id)


# Asset endpoints
@router.get("/", response_model=List[Asset])
def read_assets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    parent_id: Optional[int] = None,
    location_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[Asset]:
    """
    Retrieve assets with optional filtering.
    """
    assets = crud_asset.get_assets(
        db=db,
        skip=skip,
        limit=limit,
        asset_type=asset_type,
        status=status,
        parent_id=parent_id,
        location_id=location_id
    )
    return assets


@router.post("/", response_model=Asset)
def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_in: AssetCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Asset:
    """
    Create new asset.
    """
    # Check if asset with same code exists
    if asset_in.code:
        asset = crud_asset.get_asset_by_code(db, code=asset_in.code)
        if asset:
            raise HTTPException(
                status_code=400,
                detail="An asset with this code already exists."
            )
    
    # If parent_id is provided, verify parent exists
    if asset_in.parent_id:
        parent = crud_asset.get_asset(db, asset_id=asset_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent asset not found."
            )
    
    # If location_id is provided, verify location exists
    if asset_in.location_id:
        location = crud_asset.get_location(db, location_id=asset_in.location_id)
        if not location:
            raise HTTPException(
                status_code=404,
                detail="Location not found."
            )
    
    # If template_id is provided, verify template exists
    if asset_in.template_id:
        template = crud_asset.get_asset_template(db, template_id=asset_in.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Asset template not found."
            )
    
    asset = crud_asset.create_asset(
        db=db,
        asset=asset_in,
        created_by_id=current_user.id
    )
    return asset


@router.get("/{asset_id}", response_model=Asset)
def read_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Asset:
    """
    Get asset by ID.
    """
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    return asset


@router.get("/uuid/{uuid}", response_model=Asset)
def read_asset_by_uuid(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Asset:
    """
    Get asset by UUID.
    """
    asset = crud_asset.get_asset_by_uuid(db, uuid=uuid)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    return asset


@router.put("/{asset_id}", response_model=Asset)
def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    asset_in: AssetUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Asset:
    """
    Update an asset.
    """
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    # If code is being updated, check for duplicates
    if asset_in.code and asset_in.code != asset.code:
        existing_asset = crud_asset.get_asset_by_code(db, code=asset_in.code)
        if existing_asset:
            raise HTTPException(
                status_code=400,
                detail="An asset with this code already exists."
            )
    
    # If parent_id is being updated, verify new parent exists
    if asset_in.parent_id and asset_in.parent_id != asset.parent_id:
        parent = crud_asset.get_asset(db, asset_id=asset_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent asset not found."
            )
    
    # If location_id is being updated, verify new location exists
    if asset_in.location_id and asset_in.location_id != asset.location_id:
        location = crud_asset.get_location(db, location_id=asset_in.location_id)
        if not location:
            raise HTTPException(
                status_code=404,
                detail="Location not found."
            )
    
    # If template_id is being updated, verify new template exists
    if asset_in.template_id and asset_in.template_id != asset.template_id:
        template = crud_asset.get_asset_template(db, template_id=asset_in.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Asset template not found."
            )
    
    asset = crud_asset.update_asset(
        db=db,
        db_asset=asset,
        asset_update=asset_in
    )
    return asset


@router.delete("/{asset_id}", response_model=bool)
def delete_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete an asset.
    """
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    # Check if asset has children
    children = crud_asset.get_assets(db, parent_id=asset_id)
    if children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete asset with children. Please delete or reassign children first."
        )
    
    return crud_asset.delete_asset(db=db, asset_id=asset_id)


@router.get("/{asset_id}/hierarchy", response_model=AssetHierarchy)
def get_asset_hierarchy(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetHierarchy:
    """
    Get the complete hierarchy of an asset (all children).
    """
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    children = crud_asset.get_assets(db, parent_id=asset_id)
    return AssetHierarchy(asset=asset, children=children)


@router.get("/{asset_id}/ancestors", response_model=AssetAncestors)
def get_asset_ancestors(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetAncestors:
    """
    Get all ancestors of an asset (parent chain).
    """
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    ancestors = crud_asset.get_asset_ancestors(db, asset_id=asset_id)
    return AssetAncestors(asset=asset, ancestors=ancestors)


# AssetItem endpoints
@router.get("/{asset_id}/items/", response_model=List[AssetItem])
def read_asset_items(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[AssetItem]:
    """
    Retrieve items for a specific asset.
    """
    items = crud_asset.get_asset_items(
        db=db,
        skip=skip,
        limit=limit,
        asset_id=asset_id
    )
    return items


@router.post("/{asset_id}/items/", response_model=AssetItem)
def create_asset_item(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    item_in: AssetItemCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetItem:
    """
    Create new asset item.
    """
    # Verify asset exists
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    # Verify template exists
    template = crud_asset.get_asset_template(db, template_id=item_in.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Asset template not found"
        )
    
    # Set asset_id from path parameter
    item_data = item_in.dict()
    item_data['asset_id'] = asset_id
    
    item = crud_asset.create_asset_item(db=db, item=AssetItemCreate(**item_data))
    return item


@router.get("/items/{item_id}", response_model=AssetItem)
def read_asset_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetItem:
    """
    Get asset item by ID.
    """
    item = crud_asset.get_asset_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Asset item not found"
        )
    return item


@router.put("/items/{item_id}", response_model=AssetItem)
def update_asset_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: AssetItemUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetItem:
    """
    Update an asset item.
    """
    item = crud_asset.get_asset_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Asset item not found"
        )
    
    item = crud_asset.update_asset_item(
        db=db,
        db_item=item,
        item_update=item_in
    )
    return item


@router.delete("/items/{item_id}", response_model=bool)
def delete_asset_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete an asset item.
    """
    item = crud_asset.get_asset_item(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Asset item not found"
        )
    
    return crud_asset.delete_asset_item(db=db, item_id=item_id)


# AssetSensor endpoints
@router.get("/{asset_id}/sensors/", response_model=List[AssetSensor])
def read_asset_sensors(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[AssetSensor]:
    """
    Retrieve sensors for a specific asset.
    """
    sensors = crud_asset.get_asset_sensors(
        db=db,
        skip=skip,
        limit=limit,
        asset_id=asset_id
    )
    return sensors


@router.post("/{asset_id}/sensors/", response_model=AssetSensor)
def create_asset_sensor(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: int,
    sensor_in: AssetSensorCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetSensor:
    """
    Create new asset sensor.
    """
    # Verify asset exists
    asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
    
    # Set asset_id from path parameter
    sensor_data = sensor_in.dict()
    sensor_data['asset_id'] = asset_id
    
    sensor = crud_asset.create_asset_sensor(db=db, sensor=AssetSensorCreate(**sensor_data))
    return sensor


@router.get("/sensors/{sensor_id}", response_model=AssetSensor)
def read_asset_sensor(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetSensor:
    """
    Get asset sensor by ID.
    """
    sensor = crud_asset.get_asset_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail="Asset sensor not found"
        )
    return sensor


@router.get("/sensors/uuid/{uuid}", response_model=AssetSensor)
def read_asset_sensor_by_uuid(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetSensor:
    """
    Get asset sensor by UUID.
    """
    sensor = crud_asset.get_asset_sensor_by_uuid(db, uuid=uuid)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail="Asset sensor not found"
        )
    return sensor


@router.put("/sensors/{sensor_id}", response_model=AssetSensor)
def update_asset_sensor(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: int,
    sensor_in: AssetSensorUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> AssetSensor:
    """
    Update an asset sensor.
    """
    sensor = crud_asset.get_asset_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail="Asset sensor not found"
        )
    
    sensor = crud_asset.update_asset_sensor(
        db=db,
        db_sensor=sensor,
        sensor_update=sensor_in
    )
    return sensor


@router.delete("/sensors/{sensor_id}", response_model=bool)
def delete_asset_sensor(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> bool:
    """
    Delete an asset sensor.
    """
    sensor = crud_asset.get_asset_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail="Asset sensor not found"
        )
    
    return crud_asset.delete_asset_sensor(db=db, sensor_id=sensor_id) 