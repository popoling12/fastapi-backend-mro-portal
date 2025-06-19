from fastapi import APIRouter

from app.api.v1.endpoints   import auth, user, asset

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(asset.router, prefix="/assets", tags=["assets"])