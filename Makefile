APP_VERSION := $(shell python version.py version)

SSL_PATH := ./build/ssl
SSL_CERT_FILE := $(SSL_PATH)/localhost.pem

.PHONY: all clean test install package certificates server-wss server-ws client-dart-ws client-dart-wss test-dart-watch

# Start the development environment using tmuxinator
shell:
	tmuxinator

$(SSL_CERT_FILE):
	mkdir -p $(shell dirname $@)
	openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 \
	  -subj "/C=CM/CN=localhost" \
	  -keyout $(SSL_PATH)/localhost-key.pem \
	  -out $(SSL_CERT_FILE)

certificates: $(SSL_CERT_FILE)

server-wss: certificates
	python examples/server.py \
	  --verbose \
	  --host localhost \
	  --port 7846 \
	  --cert-file $(SSL_CERT_FILE) \
	  --key-file $(SSL_PATH)/localhost-key.pem

server-ws:
	python examples/server.py \
	  --verbose \
	  --host localhost \
	  --port 7845

client-python-ws:
	python examples/client.py \
	  --host localhost \
	  --port 7845

client-python-wss: certificates
	python examples/client.py \
	  --host localhost \
	  --port 7846 \
	  --cert-file $(SSL_CERT_FILE)

client-python-jsonrpc-ws:
	python examples/jsonrpc.py \
	  --host localhost \
	  --port 7845

client-python-jsonrpc-wss: certificates
	python examples/jsonrpc.py \
	  --host localhost \
	  --port 7846 \
	  --cert-file $(SSL_CERT_FILE)

client-dart-ws:
	dart run dart/example/ws.dart \
	  --host localhost \
	  --port 7845

client-dart-wss: certificates
	dart run dart/example/ws.dart \
	  --host localhost \
	  --port 7846 \
	  --cert-file $(SSL_CERT_FILE)

client-dart-jsonrpc-ws:
	dart run dart/example/jsonrpc.dart \
	  --host localhost \
	  --port 7845

client-dart-jsonrpc-wss: certificates
	dart run dart/example/jsonrpc.dart \
	  --host localhost \
	  --port 7846 \
	  --cert-file $(SSL_CERT_FILE)

# Run linting checks on the codebase using pre-commit
lint:
	cd dart && dart fix --dry-run
	pre-commit run --all-files --verbose

# Automatically fix any linting issues found by ruff
fix:
	ruff check . --fix
	cd dart && dart fix

test-dart:
	cd dart && dart test \
	  --chain-stack-traces \
	  --platform vm \
	  --coverage ../coverage/dart

test-python:
	pytest

test: test-dart test-python

watch-test-dart:
	nodemon -w dart -e dart -x 'make test-dart'

watch-test-python:
	nodemon -w oremi_core -e py -x 'make test-python'

watch-test:
	$(MAKE) -j2 watch-test-dart watch-test-python

# Generate a coverage report for the codebase using pytest
coverage:
	pytest --cov=oremi_core

# Generate an HTML coverage report for the codebase using pytest
coverage-html:
	pytest --cov=oremi_core --cov-report=html

install:
	poetry install
	dart pub -C dart/ get

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated

# Update dev env
update:
	poetry update
	dart pub -C dart/ upgrade
	devbox update
	pre-commit autoupdate

# Clean up build artifacts and temporary files
clean:
	rm -rf dist/ build/

# Build a distribution of the project using poetry and twine
package: clean
	poetry build
	twine check dist/*

publish-pypi: package
	twine upload --verbose -r testpypi dist/*

publish-dart:
	dart pub -C dart/ publish

publish: package
	git commit pyproject.toml -m 'Release $(APP_VERSION)'
	git tag v$(APP_VERSION)
	$(MAKE) publish-pypi
	git push --tags origin main
