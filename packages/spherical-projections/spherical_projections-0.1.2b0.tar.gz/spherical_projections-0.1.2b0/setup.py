#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# Text of the README file (if you want to include it on PyPI)
README = (HERE / "README.md").read_text() if (HERE / "README.md").exists() else ""

setup(
    name="spherical_projections",                # Package name (change as appropriate)
    version="v0.1.2-beta",                           # Package version
    description="A spherical projection library for Python",  # Short description
    long_description=README,                   # Detailed description from your README
    long_description_content_type="text/markdown",
    author="RLSGarcia",                        # Replace with your name or organization
    author_email="RLSGarcia@icloud.com",     # Replace with your email
    url="https://github.com/RobinsonGarcia/ProjectionRegistry/",  # Project URL
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),  
    include_package_data=True,                 # If you have non-Python files to include
    python_requires=">=3.7",                   # Python version requirement
    install_requires=[
        "numpy>=1.20.0",
        "pydantic>=1.10.0",
        "scipy>=1.5.0",
        "opencv-python>=4.5.0",
        # Add any other required dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # If you have console scripts or command-line utilities, you can define them here:
    # entry_points={
    #     "console_scripts": [
    #         "gnomonic=projection.cli:main",
    #     ],
    # },
)