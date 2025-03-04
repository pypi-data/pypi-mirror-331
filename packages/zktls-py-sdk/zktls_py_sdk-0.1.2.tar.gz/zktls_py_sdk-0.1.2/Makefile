.PHONY: install test lint format clean docs build check npm-install npm-clean versions

# Install all dependencies
install: npm-install
	pip install -e ".[dev,test,docs]"

# Install npm dependencies
npm-install:
	@echo "Installing Node.js dependencies..."
	npm install
	@echo "Verifying Node.js dependencies..."
	node -e "require('@primuslabs/zktls-core-sdk')"

# Clean npm artifacts
npm-clean:
	rm -rf node_modules/
	rm -f package-lock.json

# Run tests with coverage
test:
	pytest tests/ --cov=zktls --cov-report=term-missing

# Run all linting checks
lint:
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/ tests/
	pylint src/ tests/

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Clean up build artifacts
clean: npm-clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf docs/_build/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build documentation
docs:
	cd docs && make html

# Build package
build: clean
	python -m build

# Check package
check: lint test

# Show Node.js and npm versions
versions:
	@echo "Node.js version:"
	node --version
	@echo "npm version:"
	npm --version
