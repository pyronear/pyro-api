# this target runs checks on all files
quality:
	isort . -c
	flake8 ./
	mypy
	pydocstyle client/pyroclient
	black --check .

# this target runs checks on all files and potentially modifies some of them
style:
	isort .
	black .

# Build the docker
build:
	docker build src/. -t pyroapi:latest-py3.8-alpine

# Run the docker
run:
	docker-compose up -d --build

# Run the docker
stop:
	docker-compose down

# Run tests for the library
test:
	docker build src/. -t pyroapi:latest-py3.8-alpine
	docker-compose -f docker-compose-dev.yml up -d --build
	docker-compose exec -T pyroapi coverage run -m pytest tests/
	docker-compose -f docker-compose-dev.yml down

# Run tests for the Python client
client-test:
	cd client && coverage run -m pytest tests/

# Check that docs can build for client
docs:
	sphinx-build client/docs/source client/docs/_build -a
