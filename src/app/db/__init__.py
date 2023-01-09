from .init_db import *
from .models import *
from .session import *
from .tables import *


# Dependency
def get_session():
    db = SessionLocal()  # noqa: F405
    try:
        yield db
    finally:
        db.close()
