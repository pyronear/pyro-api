# this target runs checks on all files
quality:
	isort . -c
	flake8
	mypy
	pydocstyle client/pyroclient
	black --check .

# this target runs checks on all files and potentially modifies some of them
style:
	isort .
	black .

# Pin the dependencies
lock:
	poetry lock
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	poetry export -f requirements.txt --without-hashes --dev --output src/requirements-dev.txt

# Build the docker
build:
	docker build src/. -t pyroapi:python3.8-alpine3.10

# Run the docker
run:
	docker-compose up -d --build

# Run the docker
stop:
	docker-compose down

run-dev:
	docker build src/. -t pyroapi:python3.8-alpine3.10
	docker-compose -f docker-compose-dev.yml up -d --build

stop-dev:
	docker-compose -f docker-compose-dev.yml down

# Run tests for the library
test:
	docker build src/. -t pyroapi:python3.8-alpine3.10
	docker-compose -f docker-compose-dev.yml up -d --build
	docker-compose exec -T backend coverage run -m pytest tests/
	docker-compose -f docker-compose-dev.yml down

# Run tests for the Python client
test-client:
	cd client && coverage run -m pytest tests/

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a