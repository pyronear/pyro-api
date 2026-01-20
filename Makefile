DOCKER_DIR = ./docker
PYPROJECT = ./pyproject.toml
BACKEND_DIR = ./src
CLIENT_DIR = ./client
SCRIPTS_DIR = ./scripts
BACKEND_DOCKERFILE = ${BACKEND_DIR}/Dockerfile
FRONTEND_DOCKERFILE = ${FRONTEND_DIR}/Dockerfile
COMPOSE_FILE_PROD = ${DOCKER_DIR}/compose.prod.yml
COMPOSE_FILE_DEV = ${DOCKER_DIR}/compose.yml
DEPLOY_SCRIPT = ${SCRIPTS_DIR}/deploy.sh
CD_SETUP_SCRIPT = ${SCRIPTS_DIR}/setup_cd.sh
REPO_OWNER ?= pyronear
REPO_NAME ?= pyro-api
DOCKER_NAMESPACE ?= ghcr.io/${REPO_OWNER}
DOCKER_TAG ?= latest
DOCKER_PLATFORM ?= linux/amd64
REMOTE_ALIAS ?= hetzner
TMP_REQ_FILE = /tmp/requirements.txt

.PHONY: help install-backend install-frontend install-quality sync-deps venv ruff-lint ruff-lint-fix ruff-format ruff-format-fix ruff-check ruff-fix precommit typing-check deps-check quality style push-gh-secrets

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

########################################################
# Installation
########################################################

install-backend: ${PYPROJECT} ## Install the backend deps
	uv sync --locked --no-dev --no-install-project

install-test: ${PYPROJECT} ## Install the frontend deps
	uv sync --locked --no-dev --group test --no-install-project

install-quality: ${PYPROJECT} ## Install with quality dependencies
	uv sync --locked --only-dev --group quality --no-install-project

sync-deps: ${PYPROJECT} ## Install all deps
	uv sync --locked --no-dev --group test --group quality --no-install-project

venv: ${PYPROJECT}
	uv venv --python 3.11
	make sync-deps

install-client:
	uv pip install -e client/.

########################################################
# Code checks
########################################################

ruff-lint: ${PYPROJECT} ## Check code linting
	uv run ruff check . --config ${PYPROJECT}

ruff-lint-fix: ${PYPROJECT} ## Fix code linting
	uv run ruff check --fix . --config ${PYPROJECT}

ruff-format: ${PYPROJECT} ## Check code formatting
	uv run ruff format --check . --config ${PYPROJECT}

ruff-format-fix: ${PYPROJECT} ## Fix code formatting
	uv run ruff format . --config ${PYPROJECT}

ruff-check: ruff-lint ruff-format ## Check code formatting and linting

ruff-fix: ruff-lint-fix ruff-format-fix ## Fix linting & formatting issues

precommit: ${PYPROJECT} .pre-commit-config.yaml ## Run pre-commit hooks
	uv run prek run --all-files --hook-stage=pre-push

typing-check: ${PYPROJECT} ${BACKEND_DIR} ## Check type annotations
	uv run ty check .

deps-check: .github/verify_deps_sync.py ## Check dependency synchronization
	uv lock --check
	uv run --script .github/verify_deps_sync.py

# this target runs checks on all files
quality: ruff-check typing-check deps-check ## Run all quality checks

style: precommit ## Format code and run pre-commit hooks

########################################################
# Builds
########################################################

lock: ${PYPROJECT} ## Lock the backend dependencies
	uv lock

set-version: ${GLOBAL_PYPROJECT} ${BACKEND_PYPROJECT} ## Set the version in the pyproject.toml file
	uv version --frozen --no-build ${BUILD_VERSION}
	uv version --frozen --no-build --project ${BACKEND_DIR} ${BUILD_VERSION}

build-backend: ${BACKEND_DIR} ${BACKEND_DOCKERFILE} ## Build the backend container
	docker buildx build --platform ${DOCKER_PLATFORM} -f ${BACKEND_DOCKERFILE} -t ${DOCKER_NAMESPACE}/${REPO_NAME}-backend:${DOCKER_TAG} .

docker-login: ## Login to GHCR
	$(eval PAT := $(shell gh auth token))
	echo "${PAT}" | docker login ghcr.io -u ${REPO_OWNER} --password-stdin

########################################################
# Run
########################################################

check-compose: ${COMPOSE_FILE_PROD}
	docker compose --project-directory . -f ${COMPOSE_FILE_PROD} config --quiet

########################################################
# Run services
########################################################

uvicorn-backend: ${BACKEND_DIR} .env
	uv run uvicorn app.main:app --app-dir ${BACKEND_DIR} --env-file .env --reload --reload-dir ${BACKEND_DIR} --host 0.0.0.0 --port 8000 --proxy-headers --use-colors --log-level info

start-backend: build-backend ${BACKEND_DIR}
	docker run -p 8080:8080 ${DOCKER_NAMESPACE}/${REPO_NAME}-backend:${DOCKER_TAG}

stop-backend: ${BACKEND_DIR}
	docker stop ${DOCKER_NAMESPACE}/${REPO_NAME}-backend:${DOCKER_TAG}

compose-start: ${COMPOSE_FILE_DEV} .env
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} up -d --wait --build

compose-stop: ${COMPOSE_FILE_DEV}
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} down

########################################################
# Migrations
########################################################

migrations-revision: ${COMPOSE_FILE_DEV} .env
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} up -d --wait --build postgres
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} run --rm prestart alembic revision --autogenerate -m '${REVISION_MSG}'
	make compose-stop

migrations-upgrade: ${COMPOSE_FILE_DEV} .env
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} up -d --wait --build postgres
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} run --rm prestart alembic upgrade head
	make compose-stop

migrations-downgrade: ${COMPOSE_FILE_DEV} .env
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} up -d --wait --build postgres
	docker compose --project-directory . -f ${COMPOSE_FILE_DEV} run --rm prestart alembic downgrade -1
	make compose-stop

########################################################
# Client
########################################################

# Run tests for the Python client
# the "-" are used to launch the next command even if a command fail
test-client: install-client
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker compose -f docker-compose.dev.yml up -d --build --wait
	- cd client && pytest --cov=pyroclient tests/ && cd ..
	docker compose -f docker-compose.dev.yml down

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a

e2e:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker compose -f docker-compose.dev.yml up -d --build --wait
	- python scripts/test_e2e.py
	docker compose -f docker-compose.dev.yml down


########################################################
# Local setup
########################################################

# Push secrets to GH for deployment
push-secrets: .env
	gh secret set -f .env --app actions
	gh secret set -f .env --app dependabot
	gh secret set -f .env --app codespaces

########################################################
# VM Management
########################################################

# Generate SSH key, sync with GitHub and push to remote, generate PAT for docker login, acme.json
setup-cd: ${CD_SETUP_SCRIPT}
	$(eval GH_PAT := $(shell grep '^GH_PAT=' .env | cut -d'=' -f2 | tr -d "'\""))
	VM_HOST=${REMOTE_ALIAS} GH_PAT=${GH_PAT} bash ${CD_SETUP_SCRIPT}

deploy: ${COMPOSE_FILE_PROD} ${DEPLOY_SCRIPT} .env
	scp ${COMPOSE_FILE_PROD} ${REMOTE_ALIAS}:~/${REPO_NAME}/
	scp ${DEPLOY_SCRIPT} ${REMOTE_ALIAS}:~/${REPO_NAME}/
	scp .env ${REMOTE_ALIAS}:~/${REPO_NAME}/.env.prod
	ssh ${REMOTE_ALIAS}  'cd ${REPO_NAME} && bash ${DEPLOY_SCRIPT}'
