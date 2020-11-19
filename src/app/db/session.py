from sqlalchemy import create_engine
from databases import Database

from app import config as cfg


engine = create_engine(cfg.DATABASE_URL)
database = Database(cfg.DATABASE_URL)
