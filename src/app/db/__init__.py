from .init_db import *
from .models import *
from .session import *
from .tables import *


# Dependency
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
