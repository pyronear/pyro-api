# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from sqlalchemy import create_engine
from databases import Database

from app import config as cfg


engine = create_engine(cfg.DATABASE_URL)
database = Database(cfg.DATABASE_URL)
