# Alembic migrations

Alembic is the sole owner of the database schema. The application's
`init_db` only seeds the superadmin org/user; every table, column,
index and constraint is created and evolved through revision files in
`src/migrations/versions/`.

All commands assume the dev stack is running:

```shell
make run
```

## Create a new revision

After modifying a SQLModel in `src/app/models.py`, autogenerate a
revision file from the diff between your models and the live DB:

```shell
make migrate m="add active column to poses"
```

This is a thin wrapper around:

```shell
docker compose exec -T backend alembic revision --autogenerate -m "<message>"
```

The new file lands in `src/migrations/versions/`. **Always review it
before committing** — `--autogenerate` does not detect renames (it
emits drop+create), enum value additions, `server_default` changes, or
some `CHECK` constraints. Adjust by hand when needed.

## Apply pending revisions

Migrations are applied automatically when the backend container starts
(`alembic upgrade head` is the first thing in the compose command). To
apply without restarting:

```shell
make migrate-up
```

Equivalent to:

```shell
docker compose exec backend alembic upgrade head
```
