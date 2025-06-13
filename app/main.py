from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Solar Monitoring API",
    description="API for solar monitoring system",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Solar Monitoring API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routes when ready
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)