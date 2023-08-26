APP_VERSION := $(shell python version.py)

.PHONY: all clean test install package build/packages/oremi-core-$(APP_VERSION)

# Start the development environment using tmuxinator
env:
	tmuxinator

# Run linting checks on the codebase using pre-commit
lint:
	pre-commit run --all-files --verbose

# Automatically fix any linting issues found by ruff
fix:
	ruff check . --fix

# Run tests using pytest
test:
	pytest

# Generate a coverage report for the codebase using pytest
coverage:
	pytest --cov=oremi

# Generate an HTML coverage report for the codebase using pytest
coverage-html:
	pytest --cov=oremi --cov-report=html

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated

# Update dev env
update:
	poetry update
	nix flake update
	pre-commit autoupdate

# Clean up build artifacts and temporary files
clean:
	rm -rf dist/

build/packages/oremi-core-$(APP_VERSION):
	mkdir -p $(shell dirname $@)
	nix build -v . --out-link $@

package: build/packages/oremi-core-$(APP_VERSION)

# Build a distribution of the project using poetry and twine
dist: clean
	poetry build
	twine check dist/*

# Publish a distribution of the project to TestPyPI using twine
publish: dist
	twine upload --verbose -r testpypi dist/*

install:
	poetry install
