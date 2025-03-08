# Open_Recall Makefile
# Provides shortcuts for common development and packaging tasks

.PHONY: run_desktop run_web_dev build_desktop package_desktop install-dev pypi-build pypi-upload clean dist

# Default target
help:
	@echo "Open_Recall Makefile"
	@echo "==================="
	@echo ""
	@echo "Available commands:"
	@echo "  make run_desktop         - Run the application in development mode"
	@echo "  make run_web_dev         - Run the application with hot reloading"
	@echo "  make build_desktop       - Build the application with Briefcase"
	@echo "  make package_desktop     - Package the application as an installer"
	@echo "  make install-dev         - Install package in development mode"
	@echo "  make pypi-build          - Build the Python package for PyPI"
	@echo "  make pypi-upload         - Upload the package to PyPI"
	@echo "  make clean               - Clean build artifacts"
	@echo ""

# Run the application as desktop app
run_desktop:
	python -m open_recall.app

# Run the application as web server
run_web_dev:
	python -m open_recall.main

# Backup and modify __main__.py for desktop app
prepare_desktop_main:
	@echo "Backing up __main__.py..."
	@copy open_recall\__main__.py open_recall\__main__.py.bak
	@echo "Updating __main__.py for desktop app..."
	@echo import sys > open_recall\__main__.py
	@echo from open_recall.app import main >> open_recall\__main__.py
	@echo. >> open_recall\__main__.py
	@echo if __name__ == "__main__": >> open_recall\__main__.py
	@echo     sys.exit(main^(^)) >> open_recall\__main__.py

# Restore original __main__.py
restore_main:
	@echo "Restoring original __main__.py..."
	@copy open_recall\__main__.py.bak open_recall\__main__.py
	@del open_recall\__main__.py.bak

# Run the application in briefcase dev mode
run_desktop_dev: prepare_desktop_main
	briefcase dev
	$(MAKE) restore_main

# Build the application with Briefcase
build_desktop: prepare_desktop_main
	briefcase create
	briefcase build
	$(MAKE) restore_main

# Package the application as an installer
package_desktop: clean prepare_desktop_main
	briefcase create
	briefcase build
	briefcase package
	$(MAKE) restore_main

# Install package in development mode
install-dev:
	pip install -e .

# Build the Python package for PyPI
pypi-build: clean
	python -m pip install --upgrade build
	python -m build

# Upload the package to PyPI
pypi-upload: clean pypi-build
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
	@for /d %%i in (*egg-info) do @if exist "%%i" rmdir /s /q "%%i"
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
