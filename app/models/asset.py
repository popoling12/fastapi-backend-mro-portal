from enum import Enum
import uuid
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, JSON, Enum as SQLEnum, Float, event, text
)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.user import User  # Adjust import path as needed


class AssetType(str, Enum):
    """Types of assets in the solar plant hierarchy"""
    PLANT = "plant"
    SUB_PLANT = "sub_plant"
    INVERTER = "inverter"
    STRING = "string"
    PANEL = "panel"
    SENSOR = "sensor"


class AssetStatus(str, Enum):
    """Lifecycle status of an asset"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class TemplateCategory(str, Enum):
    """Category for asset templates"""
    HARDWARE = "hardware"
    CONSUMABLE = "consumable"
    LICENSE = "license"


class Location(Base):
    """
    Hierarchical locations where assets can be deployed
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=True, index=True)
    description = Column(String(500), nullable=True)

    parent_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    parent = relationship("Location", remote_side=[id], backref="children")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"


class AssetTemplate(Base):
    """
    Catalog of asset types available for purchase/store
    """
    __tablename__ = "asset_templates"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=True, index=True)  # SKU or part number
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    category = Column(SQLEnum(TemplateCategory), nullable=False, default=TemplateCategory.HARDWARE)

    manufacturer = Column(String(100), nullable=True)
    model_number = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    default_config = Column(JSON, default=dict, nullable=True)
    unit_price = Column(Float, nullable=True)
    license_duration_days = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    deployed_items = relationship("AssetItem", back_populates="template")

    def __repr__(self):
        return f"<AssetTemplate(id={self.id}, code='{self.code}', name='{self.name}', category='{self.category}')>"


class StoreInventory(Base):
    """
    Tracks stock of asset templates in store
    """
    __tablename__ = "store_inventory"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("asset_templates.id"), nullable=False)
    template = relationship("AssetTemplate", backref="inventory_entries")

    quantity = Column(Integer, default=0, nullable=False)
    storage_location = Column(String(200), nullable=True)
    last_restocked = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<StoreInventory(template_id={self.template_id}, qty={self.quantity})>"


class Asset(Base):
    """
    Deployed assets, linked to templates and locations
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    template_id = Column(Integer, ForeignKey("asset_templates.id"), nullable=True)
    template = relationship("AssetTemplate", lazy="joined")

    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=True, index=True)
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False)

    parent_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    parent = relationship("Asset", remote_side=[id], backref="children")

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    location = relationship("Location", backref="assets")

    installation_date = Column(DateTime(timezone=True), nullable=True)
    config = Column(JSON, default=dict, nullable=True)
    realtime_data_tag = Column(String(200), nullable=True)

    deployed_items = relationship("AssetItem", back_populates="asset")
    sensors = relationship("AssetSensor", back_populates="asset")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.asset_type}', location_id={self.location_id})>"


class AssetItem(Base):
    """
    Represents consumables or licenses deployed to an asset
    """
    __tablename__ = "asset_items"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("asset_templates.id"), nullable=False)

    quantity = Column(Integer, default=1, nullable=False)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("Asset", back_populates="deployed_items")
    template = relationship("AssetTemplate", back_populates="deployed_items")

    def __repr__(self):
        return f"<AssetItem(asset_id={self.asset_id}, template_id={self.template_id}, qty={self.quantity})>"


class AssetSensor(Base):
    """
    Represents sensors attached to an asset
    """
    __tablename__ = "asset_sensors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    asset = relationship("Asset", back_populates="sensors")

    name = Column(String(200), nullable=False)
    sensor_path = Column(String(200), nullable=False)
    system_source = Column(String(100), nullable=False)
    config = Column(JSON, default=dict, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<AssetSensor(id={self.id}, name='{self.name}', asset_id={self.asset_id})>"


# Auto-populate asset fields from template on insert
@event.listens_for(Asset, 'before_insert')
def apply_template_defaults(mapper, connection, target):
    if target.template_id:
        session = Session.object_session(target)
        if session:
            tmpl = session.get(AssetTemplate, target.template_id)
            if tmpl:
                target.name = target.name or tmpl.name
                target.asset_type = tmpl.asset_type
                if not target.config:
                    target.config = tmpl.default_config.copy() if tmpl.default_config else {}

# Auto-set expiry for license items
@event.listens_for(AssetItem, 'before_insert')
def apply_license_expiry(mapper, connection, target):
    session = Session.object_session(target)
    tmpl = None
    if session and target.template_id:
        tmpl = session.get(AssetTemplate, target.template_id)
    if tmpl and tmpl.category == TemplateCategory.LICENSE and tmpl.license_duration_days:
        target.expires_at = text(f"now() + interval '{tmpl.license_duration_days} days'")
