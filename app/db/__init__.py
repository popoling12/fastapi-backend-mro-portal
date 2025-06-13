from .base import Base
from .session import SessionLocal, engine

# This line is to ensure that all models are imported and registered with SQLAlchemy's metadata
# before Base.metadata.create_all is called.
from app.models import user  # Import to register model