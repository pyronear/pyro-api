PYTHON_VERSION ?= 3.11
PYPROJECT := pyproject.toml
BACKEND_IMAGE ?= pyronear/alert-api:latest
COMPOSE_DEV := docker-compose.dev.yml

.PHONY: sync-deps venv install-backend install-quality install-test install-client-test install-docs install-e2e
.PHONY: ruff-lint ruff-lint-fix ruff-format ruff-format-fix ruff-check ruff-fix typing-check deps-check quality style precommit
.PHONY: lock build build-backend run run-dev stop migrate migrate-up test build-client test-client docs-client e2e uvicorn-backend

sync-deps: $(PYPROJECT)
	uv sync --locked --all-groups --all-packages --no-install-project

venv: $(PYPROJECT)
	uv venv --python $(PYTHON_VERSION) --allow-existing
	$(MAKE) sync-deps

install-backend: $(PYPROJECT)
	uv sync --locked --only-group server --no-install-project

install-quality: $(PYPROJECT)
	uv sync --locked --group server --group client --group quality --no-install-project

install-test: $(PYPROJECT)
	uv sync --locked --group server --group test --no-install-project

install-client-test: $(PYPROJECT)
	uv sync --locked --group client-test --no-install-project

install-docs: $(PYPROJECT)
	uv sync --locked --group docs --no-install-project

install-e2e: $(PYPROJECT)
	uv sync --locked --group e2e --no-install-project

ruff-lint: $(PYPROJECT)
	uv run --group quality ruff check . --config $(PYPROJECT)

ruff-lint-fix: $(PYPROJECT)
	uv run --group quality ruff check --fix . --config $(PYPROJECT)

ruff-format: $(PYPROJECT)
	uv run --group quality ruff format --check . --config $(PYPROJECT)

ruff-format-fix: $(PYPROJECT)
	uv run --group quality ruff format . --config $(PYPROJECT)

ruff-check: ruff-lint ruff-format

ruff-fix: ruff-lint-fix ruff-format-fix

typing-check: $(PYPROJECT)
	uv run --group server --group client --group quality ty check src/app client/pyroclient

deps-check: .github/verify_deps_sync.py
	uv lock --check
	uv run --script .github/verify_deps_sync.py

quality: ruff-check typing-check deps-check

style: precommit

precommit: $(PYPROJECT) .pre-commit-config.yaml
	uv run --group quality prek run --all-files --hook-stage=pre-push

lock: $(PYPROJECT)
	uv lock

build: build-backend

build-backend:
	docker build -f src/Dockerfile . -t $(BACKEND_IMAGE)

run:
	docker compose up -d --build --wait

run-dev: run

stop:
	docker compose down

migrate:
	@if [ -z "$(m)" ]; then echo "Usage: make migrate m=\"short description\""; exit 1; fi
	docker compose exec -T backend alembic revision --autogenerate -m "$(m)"

migrate-up:
	docker compose exec -T backend alembic upgrade head

test:
	UV_GROUPS="server test" docker compose -f $(COMPOSE_DEV) up -d --build --wait
	- docker compose -f $(COMPOSE_DEV) exec -T backend pytest --cov=app
	docker compose -f $(COMPOSE_DEV) down

build-client:
	uv sync --locked --group client --no-install-project

test-client: build-client
	docker compose -f $(COMPOSE_DEV) up -d --build --wait
	- SUPERADMIN_LOGIN=superadmin_login SUPERADMIN_PWD=superadmin_pwd uv run --group client-test pytest --cov=pyroclient client/tests/
	docker compose -f $(COMPOSE_DEV) down

docs-client:
	uv run --group docs sphinx-build client/docs/source client/docs/_build -a

e2e:
	docker compose -f $(COMPOSE_DEV) up -d --build --wait
	- uv run --group e2e python scripts/test_e2e.py
	docker compose -f $(COMPOSE_DEV) down

uvicorn-backend:
	PYTHONPATH=src uv run --group server uvicorn app.main:app --reload --host 0.0.0.0 --port 5050 --proxy-headers
