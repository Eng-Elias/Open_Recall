#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

# This setup.py file is maintained for backward compatibility
# Most configuration is now in pyproject.toml

with io.open("open_recall/__init__.py", encoding="utf8") as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

# Use setuptools.setup() for backward compatibility
# The actual configuration is in pyproject.toml
setup(
    packages=find_packages(exclude=["logs", "test_venv", "venv", "build", "dist", "*.egg-info"]),
    include_package_data=True,
)
