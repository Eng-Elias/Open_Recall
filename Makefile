# OpenRecall Makefile
# Provides shortcuts for common development and packaging tasks

.PHONY: run dev build package pypi-build pypi-upload clean help

# Default target
help:
	@echo "OpenRecall Makefile"
	@echo "==================="
	@echo ""
	@echo "Available commands:"
	@echo "  make run         - Run the application in development mode"
	@echo "  make dev         - Run the application with hot reloading"
	@echo "  make build       - Build the application with Briefcase"
	@echo "  make package     - Package the application as an installer"
	@echo "  make pypi-build  - Build the Python package for PyPI"
	@echo "  make pypi-upload - Upload the package to PyPI"
	@echo "  make clean       - Clean build artifacts"
	@echo ""

# Run the application in development mode
run:
	python -m open_recall.app

# Run the application with hot reloading
dev:
	python -m open_recall.main

# Build the application with Briefcase
build:
	briefcase create
	briefcase build

# Package the application as an installer
package:
	briefcase create
	briefcase build
	briefcase package

# Build the Python package for PyPI
pypi-build:
	python -m pip install --upgrade build
	python -m build

# Upload the package to PyPI
pypi-upload:
	python -m pip install --upgrade twine
	python -m twine upload dist/*

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
