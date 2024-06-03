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

# Run tests for the library
test:
	-poetry export -f requirements.txt --without-hashes --with test --output requirements.txt
	-docker compose -f docker-compose.dev.yml up -d --build --wait
	-sleep 30
	-docker compose exec -T backend pytest --cov=app
	-docker compose -f docker-compose.dev.yml down

# Run tests for the Python client
test-client:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker compose -f docker-compose.dev.yml up -d --build --wait
	cd client && pytest --cov=pyroclient tests/ && cd ..
	docker compose -f docker-compose.dev.yml down

# Check that docs can build for client
docs-client:
	sphinx-build client/docs/source client/docs/_build -a


e2e:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
	docker compose -f docker-compose.dev.yml up -d --build --wait
	python scripts/test_e2e.py
	docker compose -f docker-compose.dev.yml down
