from .base import Base
from .session import SessionLocal, engine

# This line is to ensure that all models are imported an registered with SQLAlchemy's metadata
# before Base.metadata.create_all is called.
# For now, we don't have models in app.models yet, but this is a common pattern.
# from app.models import * # noqa F401, F403 - Uncomment when models exist.
