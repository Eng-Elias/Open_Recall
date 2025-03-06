#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

with io.open("README.md", encoding="utf8") as readme:
    long_description = readme.read()

with io.open("open_recall/__init__.py", encoding="utf8") as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="openrecall",
    version=version,
    description="A screenshot capture and management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenRecall Team",
    author_email="info@openrecall.com",
    license="MIT",
    packages=find_packages(
        exclude=[
            "docs",
            "tests",
            "windows",
            "macOS",
            "linux",
            "iOS",
            "android",
            "django",
        ]
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "jinja2>=3.1.2",
        "sqlalchemy>=2.0.7",
        "pillow>=9.5.0",
        "mss>=9.0.1",
        "pywin32>=306",
        "psutil>=5.9.4",
        "python-multipart>=0.0.6",
        "alembic>=1.10.2",
        "toga>=0.4.0",
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
    package_data={
        "open_recall": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
            "static/js/libs/*.js",
            "static/images/*.*",
            "static/images/icon/*.*",
        ],
    },
    include_package_data=True,
)
