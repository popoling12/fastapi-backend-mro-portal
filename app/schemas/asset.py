from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.asset import AssetType, AssetStatus, TemplateCategory


# Location schemas
class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None


class Location(LocationBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AssetTemplate schemas
class AssetTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    asset_type: AssetType
    category: TemplateCategory = TemplateCategory.HARDWARE
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_config: Optional[Dict[str, Any]] = None
    unit_price: Optional[float] = None
    license_duration_days: Optional[int] = None


class AssetTemplateCreate(AssetTemplateBase):
    pass


class AssetTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    asset_type: Optional[AssetType] = None
    category: Optional[TemplateCategory] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_config: Optional[Dict[str, Any]] = None
    unit_price: Optional[float] = None
    license_duration_days: Optional[int] = None


class AssetTemplate(AssetTemplateBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# StoreInventory schemas
class StoreInventoryBase(BaseModel):
    template_id: int
    quantity: int = Field(..., ge=0)
    storage_location: Optional[str] = Field(None, max_length=200)


class StoreInventoryCreate(StoreInventoryBase):
    pass


class StoreInventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    storage_location: Optional[str] = Field(None, max_length=200)


class StoreInventory(StoreInventoryBase):
    id: int
    last_restocked: datetime
    template: AssetTemplate

    class Config:
        from_attributes = True


# Asset schemas
class AssetBase(BaseModel):
    template_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    asset_type: AssetType
    status: AssetStatus = AssetStatus.ACTIVE
    parent_id: Optional[int] = None
    location_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    realtime_data_tag: Optional[str] = Field(None, max_length=200)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    template_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=100)
    asset_type: Optional[AssetType] = None
    status: Optional[AssetStatus] = None
    parent_id: Optional[int] = None
    location_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    realtime_data_tag: Optional[str] = Field(None, max_length=200)


class Asset(AssetBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    template: Optional[AssetTemplate] = None
    location: Optional[Location] = None
    parent: Optional['Asset'] = None
    children: List['Asset'] = []
    deployed_items: List['AssetItem'] = []
    sensors: List['AssetSensor'] = []

    class Config:
        from_attributes = True


# AssetItem schemas
class AssetItemBase(BaseModel):
    asset_id: int
    template_id: int
    quantity: int = Field(..., ge=1)
    expires_at: Optional[datetime] = None


class AssetItemCreate(AssetItemBase):
    pass


class AssetItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)
    expires_at: Optional[datetime] = None


class AssetItem(AssetItemBase):
    id: int
    deployed_at: datetime
    asset: Asset
    template: AssetTemplate

    class Config:
        from_attributes = True


# AssetSensor schemas
class AssetSensorBase(BaseModel):
    asset_id: int
    name: str = Field(..., min_length=1, max_length=200)
    sensor_path: str = Field(..., min_length=1, max_length=200)
    system_source: str = Field(..., min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None


class AssetSensorCreate(AssetSensorBase):
    pass


class AssetSensorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sensor_path: Optional[str] = Field(None, min_length=1, max_length=200)
    system_source: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None


class AssetSensor(AssetSensorBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    asset: Asset

    class Config:
        from_attributes = True


# Hierarchy schemas
class AssetHierarchy(BaseModel):
    asset: Asset
    children: List[Asset]

    class Config:
        from_attributes = True


class AssetAncestors(BaseModel):
    asset: Asset
    ancestors: List[Asset]

    class Config:
        from_attributes = True


# Update forward references
Asset.model_rebuild()
AssetItem.model_rebuild()
AssetSensor.model_rebuild() 