from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Ensure SQLALCHEMY_DATABASE_URL is a string for create_engine
if settings.SQLALCHEMY_DATABASE_URL:
    db_url = str(settings.SQLALCHEMY_DATABASE_URL)
else:
    # This case should ideally not happen if settings validation is correct
    # and environment variables are set.
    # Fallback or raise an error. For now, let's assume it's always provided.
    # Consider raising an ImproperlyConfigured error or similar if it can be None here.
    raise ValueError("SQLALCHEMY_DATABASE_URL is not configured properly.")

engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
