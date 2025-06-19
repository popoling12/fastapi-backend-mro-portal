from typing import Dict
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.models.asset import AssetType, AssetStatus
from app.tests.utils.utils import get_superuser_token_headers
from app.tests.utils.asset import create_random_asset


def test_create_asset(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test creating a new asset"""
    data = {
        "name": "Test Plant",
        "code": "TEST001",
        "asset_type": AssetType.PLANT,
        "status": AssetStatus.ACTIVE,
        "location": "Test Location",
        "installation_date": datetime.now().isoformat(),
        "manufacturer": "Test Manufacturer",
        "model_number": "TEST-MODEL-001",
        "config": {"capacity_mw": 100}
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/assets/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["code"] == data["code"]
    assert content["asset_type"] == data["asset_type"]
    assert content["status"] == data["status"]
    assert "id" in content
    assert "uuid" in content


def test_read_asset(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test reading an asset"""
    asset = create_random_asset(db)
    
    response = client.get(
        f"{settings.API_V1_STR}/assets/{asset.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == asset.name
    assert content["code"] == asset.code
    assert content["id"] == asset.id


def test_read_asset_by_uuid(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test reading an asset by UUID"""
    asset = create_random_asset(db)
    
    response = client.get(
        f"{settings.API_V1_STR}/assets/uuid/{asset.uuid}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == asset.name
    assert content["code"] == asset.code
    assert content["uuid"] == asset.uuid


def test_read_assets(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test reading multiple assets"""
    # Create multiple assets
    for _ in range(3):
        create_random_asset(db)
    
    response = client.get(
        f"{settings.API_V1_STR}/assets/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 3


def test_read_assets_with_filters(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test reading assets with filters"""
    # Create assets with different types
    create_random_asset(db, asset_type=AssetType.PLANT)
    create_random_asset(db, asset_type=AssetType.INVERTER)
    
    # Test filtering by asset type
    response = client.get(
        f"{settings.API_V1_STR}/assets/?asset_type={AssetType.PLANT}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert all(asset["asset_type"] == AssetType.PLANT for asset in content)
    
    # Test filtering by status
    response = client.get(
        f"{settings.API_V1_STR}/assets/?status={AssetStatus.ACTIVE}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert all(asset["status"] == AssetStatus.ACTIVE for asset in content)


def test_update_asset(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test updating an asset"""
    asset = create_random_asset(db)
    
    data = {
        "name": "Updated Asset",
        "status": AssetStatus.MAINTENANCE,
        "config": {"capacity_mw": 200}
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/assets/{asset.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["status"] == data["status"]
    assert content["config"] == data["config"]
    assert content["code"] == asset.code  # Unchanged fields should remain


def test_delete_asset(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test deleting an asset"""
    asset = create_random_asset(db)
    
    response = client.delete(
        f"{settings.API_V1_STR}/assets/{asset.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify asset is deleted
    response = client.get(
        f"{settings.API_V1_STR}/assets/{asset.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_get_asset_hierarchy(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test getting asset hierarchy"""
    # Create parent asset
    parent = create_random_asset(db, asset_type=AssetType.PLANT)
    
    # Create child asset
    child = create_random_asset(
        db,
        asset_type=AssetType.SUB_PLANT,
        parent_id=parent.id
    )
    
    response = client.get(
        f"{settings.API_V1_STR}/assets/{parent.id}/hierarchy",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["asset"]["id"] == parent.id
    assert len(content["children"]) == 2  # Parent and child


def test_get_asset_ancestors(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test getting asset ancestors"""
    # Create grandparent asset
    grandparent = create_random_asset(db, asset_type=AssetType.PLANT)
    
    # Create parent asset
    parent = create_random_asset(
        db,
        asset_type=AssetType.SUB_PLANT,
        parent_id=grandparent.id
    )
    
    # Create child asset
    child = create_random_asset(
        db,
        asset_type=AssetType.INVERTER,
        parent_id=parent.id
    )
    
    response = client.get(
        f"{settings.API_V1_STR}/assets/{child.id}/ancestors",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["asset"]["id"] == child.id
    assert len(content["ancestors"]) == 2  # Parent and grandparent 