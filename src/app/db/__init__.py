from .tables import *
from .session import engine, database, Base, SessionLocal
from .init_db import init_db
from .models import AccessType, EventType, MediaType, SiteType


# Dependency
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
