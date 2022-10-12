# this target runs checks on all files
quality:
	isort . -c
	mypy
	pydocstyle pyroclient
	black --check .

# this target runs checks on all files and potentially modifies some of them
style:
	isort .
	black .

# Run tests for the library
test:
	coverage run -m pytest tests/

# Check that docs can build for client
docs-client:
	sphinx-build docs/source docs/_build -a