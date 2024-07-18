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
	docker build src/. -t pyronear/pyro-api:python3.9-alpine3.14
	docker build src/. -t pyronear/pyro-api:latest

# Run the docker
run:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker compose up -d --build

# Run the docker
stop:
	docker compose down

run-dev:
	poetry export -f requirements.txt --without-hashes --with dev --output src/app/requirements.txt
	docker compose -f docker-compose.test.yml up -d --build
	docker compose exec localstack awslocal s3 mb s3://bucket
	docker compose exec localstack awslocal s3api put-object --bucket bucket --key media-folder

stop-dev:
	docker compose -f docker-compose.test.yml down

# Run tests for the library
test:
	poetry export -f requirements.txt --without-hashes --with dev --output src/app/requirements.txt
	docker compose -f docker-compose.test.yml up -d --build --wait
	sleep 20
	docker compose exec -T backend pytest -s tests/routes/test_events.py::test_fetch_unacknowledged_events

# Run tests for the Python client
test-client:
	cd client && pytest --cov=pyroclient tests/ -n auto

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a
