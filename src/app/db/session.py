# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config as cfg

__all__ = ["SessionLocal", "database", "engine"]

engine = create_engine(cfg.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database = Database(cfg.DATABASE_URL)
