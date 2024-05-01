# this target runs checks on all files
quality:
	ruff format --check .
	ruff check .
	mypy

# this target runs checks on all files and potentially modifies some of them
style:
	ruff format .
	ruff check --fix .

# Pin the dependencies
lock:
	poetry lock --no-update

# Build the docker
build:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker build -f src/Dockerfile . -t pyronear/alert-api:latest

# Run the docker
run:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker compose up -d --build --wait

# Run the docker
stop:
	docker compose down

run-dev:
	poetry export -f requirements.txt --without-hashes --with test --output requirements.txt
	docker compose -f docker-compose.dev.yml -f docker-compose.override.yml up -d --build --wait
	docker compose exec localstack awslocal s3 mb s3://sample-bucket
	docker compose exec localstack awslocal s3api put-object --bucket sample-bucket --key media-folder

stop-dev:
	docker compose -f docker-compose.dev.yml down

# Run tests for the library
test:
	poetry export -f requirements.txt --without-hashes --with test --output requirements.txt
	docker compose -f docker-compose.dev.yml up -d --build
	docker compose exec localstack awslocal s3 mb s3://sample-bucket
	docker compose exec -T backend pytest --cov=app
	docker compose -f docker-compose.dev.yml down

# Run tests for the Python client
test-client:
	cd client && pytest --cov=pyroclient tests/ -n auto

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a
