# Alembic main commands

All commands should be run after spinning the containers using

```shell
docker compose up -d db backend
```

## Create a revision

Alembic allows you to record migration operation using DB operations. Let's create a revision file:

```shell
docker compose exec -T backend alembic revision --autogenerate
```

Once generated, you should edit the revision file in src/migrations/versions that was created. See example [here](https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/blob/main/fastapi-alembic-sqlmodel-async/alembic/versions/2022-09-25-19-46_60d49bf413b8.py).

## Apply revisions

Now apply all the revisions

```shell
docker compose exec backend alembic upgrade head
```

## One-time reset (migrating past the 2026-04 baseline)

In April 2026 the migration history was collapsed into a single `initial` baseline (`9700bbccb2f1`). Any database that was previously migrated under the old history still carries a stale `alembic_version` row pointing to a deleted revision, which will make `alembic upgrade head` fail.

Before starting the backend against such a database, run **once**:

```shell
psql "$POSTGRES_URL" -c "DELETE FROM alembic_version;"
alembic stamp head
```

This only updates the version marker — no DDL runs. Fresh databases do not need this step; they will be created by `alembic upgrade head` on first boot.
