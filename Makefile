# this target runs checks on all files
quality:
	ruff check .
	mypy
	black --check .
	bandit -r . -c pyproject.toml

# this target runs checks on all files and potentially modifies some of them
style:
	black .
	ruff --fix .

# Pin the dependencies
lock:
	poetry lock

# Build the docker
build:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker build src/. -t pyronear/pyro-api:python3.8-alpine3.10-prod

# Run the docker
run:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker-compose up -d --build

# Run the docker
stop:
	docker-compose down

run-dev:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker build src/. -t pyronear/pyro-api:python3.8-alpine3.10
	poetry export -f requirements.txt --without-hashes --with dev --output src/requirements-dev.txt
	docker-compose -f docker-compose-dev.yml up -d --build

stop-dev:
	docker-compose -f docker-compose-dev.yml down

# Run tests for the library
test:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker build src/. -t pyronear/pyro-api:python3.8-alpine3.10
	poetry export -f requirements.txt --without-hashes --with dev --output src/requirements-dev.txt
	docker-compose -f docker-compose-dev.yml up -d --build
	docker-compose exec -T backend coverage run -m pytest tests/
	docker-compose -f docker-compose-dev.yml down

# Run tests for the Python client
test-client:
	cd client && coverage run -m pytest tests/

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a
