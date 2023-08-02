# this target runs checks on all files
quality:
	isort . -c
	flake8
	mypy
	pydocstyle
	black --check .
	bandit -r . -c pyproject.toml
	autoflake -r .

# this target runs checks on all files and potentially modifies some of them
style:
	isort .
	black .
	autoflake --in-place -r .

# Pin the dependencies
lock:
	poetry lock
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	poetry export -f requirements.txt --without-hashes --with dev --output src/requirements-dev.txt

# Build the docker
build:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker build src/. -t pyronear/pyro-api:python3.8-alpine3.10

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
	# NOTE: sleep to make sure localstack is up and running
	while ! nc -z localhost 4566; do sleep 1; done
	# NOTE: should be docker-compose commands.
	docker-compose exec localstack awslocal s3 mb s3://sample-bucket
	docker-compose exec localstack awslocal s3api put-object --bucket sample-bucket --key media-folder

stop-dev:
	docker-compose -f docker-compose-dev.yml down

# Run tests for the library
test:
	poetry export -f requirements.txt --without-hashes --output src/app/requirements.txt
	docker build src/. -t pyronear/pyro-api:python3.8-alpine3.10
	poetry export -f requirements.txt --without-hashes --with dev --output src/requirements-dev.txt
	docker-compose -f docker-compose-dev.yml up -d --build
	# NOTE: sleep to make sure localstack is up and running
	while ! nc -z localhost 4566; do sleep 1; done
	docker-compose exec localstack awslocal s3 mb s3://sample-bucket
	docker-compose exec -T backend coverage run -m pytest tests/
	docker-compose -f docker-compose-dev.yml down

# Run tests for the Python client
test-client:
	cd client && coverage run -m pytest tests/

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a
