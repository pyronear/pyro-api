from .init_db import init_db
from .models import AccessType, EventType, MediaType, SiteType
from .session import Base, SessionLocal, database, engine
from .tables import *


# Dependency
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
