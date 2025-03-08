# OpenRecall Makefile
# Provides shortcuts for common development and packaging tasks

.PHONY: run dev build package pypi-build pypi-upload clean help

# Default target
help:
	@echo "OpenRecall Makefile"
	@echo "==================="
	@echo ""
	@echo "Available commands:"
	@echo "  make run_desktop         - Run the application in development mode"
	@echo "  make run_web_dev         - Run the application with hot reloading"
	@echo "  make build_desktop       - Build the application with Briefcase"
	@echo "  make package_desktop     - Package the application as an installer"
	@echo "  make pypi-build          - Build the Python package for PyPI"
	@echo "  make pypi-upload         - Upload the package to PyPI"
	@echo "  make clean               - Clean build artifacts"
	@echo ""

# Run the application in development mode
run_desktop:
	python -m open_recall.app

# Run the application with hot reloading
run_web_dev:
	python -m open_recall.main

# Build the application with Briefcase
build_desktop:
	briefcase create
	briefcase build

# Package the application as an installer
package_desktop:
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
clean_linux:
	@echo "Cleaning build artifacts on Linux/macOS..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find open_recall -type d -name __pycache__ -exec rm -rf {} +
	find open_recall -type f -name "*.pyc" -delete
	find open_recall -type f -name "*.pyo" -delete
	find open_recall -type f -name "*.pyd" -delete
	find open_recall -type f -name ".coverage" -delete
	find open_recall -type d -name "*.egg-info" -exec rm -rf {} +
	find open_recall -type d -name "*.egg" -exec rm -rf {} +
	rm -rf open_recall/data/screenshots/*
	rm -f open_recall/openrecall.db

clean_windows:
	@echo "Cleaning build artifacts on Windows..."
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@if exist *.egg-info rmdir /s /q *.egg-info
	@echo "Removing __pycache__ directories in open_recall..."
	@for /d /r open_recall %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@echo "Removing compiled Python files in open_recall..."
	@del /s /q open_recall\*.pyc 2>nul || echo No .pyc files found
	@del /s /q open_recall\*.pyo 2>nul || echo No .pyo files found
	@del /s /q open_recall\*.pyd 2>nul || echo No .pyd files found
	@del /s /q open_recall\.coverage 2>nul || echo No .coverage files found
	@echo "Cleaning application data..."
	@if exist open_recall\data\screenshots rmdir /s /q open_recall\data\screenshots
	@if not exist open_recall\data mkdir open_recall\data
	@if not exist open_recall\data\screenshots mkdir open_recall\data\screenshots
	@echo "Created empty screenshots directory"
	@if exist open_recall\openrecall.db del /q open_recall\openrecall.db
	@echo "Clean completed successfully!"

# Main clean command that detects OS
ifeq ($(OS),Windows_NT)
clean:
	@echo "Detected Windows environment"
	@$(MAKE) clean_windows
else
clean:
	@echo "Detected Unix-like environment"
	@$(MAKE) clean_linux
endif
