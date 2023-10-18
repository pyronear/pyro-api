# Alembic main commands

Following main guidelines, following commands should be run within a running container using docker-compose: `$ PORT=8002 docker-compose exec -T web alembic ...`

## Create a revision

A revision is the equivalent of a programmatic state of the Database.
You can try to generate it automatically (https://alembic.sqlalchemy.org/en/latest/autogenerate.html) and review it manually:
```shell
docker compose exec -T backend alembic revision --autogenerate -m "Add account ts column"
```

Or manually if that fails. Generate the revision Python file with the following and then implement the `upgrade()` & `downgrade()` functions using SQLAlchemy operations (op.create_table, op.add_column, etc.):
```shell
docker compose exec -T backend alembic revision -m "Add account ts column"
```

## Run the migration

Now that the upgrade and downgrade functions have been implemented, you can switch from one version to the next like Git history.

```shell
docker compose exec -T backend alembic upgrade head
```
