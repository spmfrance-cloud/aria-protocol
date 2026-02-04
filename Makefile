.PHONY: install test demo clean

# Install the package in development mode
install:
	pip install -e .

# Install with development dependencies
install-dev:
	pip install -e ".[dev]"

# Run all tests
test:
	pytest

# Run tests with verbose output
test-verbose:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=aria --cov-report=term-missing

# Run the demo
demo:
	python examples/demo.py

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf aria/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .coverage
	rm -rf htmlcov/

# Show help
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  demo         - Run the demo script"
	@echo "  clean        - Remove build artifacts"
