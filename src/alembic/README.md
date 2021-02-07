[comment]: <> (TODO write migration guide/contributing with docker-compose commands)

# Alembic main commands

## Manually created revision

-> `$ alembic revision -m "create account table"`<br/>
generates template "alembic/{id}_create_account_table.py"

-> implement `upgrade()` & `downgrade()` functions using SQLAlchemy operations (op.create_table, op.add_column, etc.)

-> `$ alembic upgrade head`
applies all pending revisions to database


## Auto generated revision
**Alternative** using auto generated revision (https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

-> `$ alembic revision --autogenerate -m "Add account ts column"`
generates filled "alembic/{id}_add_account_ts_column.py"

-> review and adjust generated script