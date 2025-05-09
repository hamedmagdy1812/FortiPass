#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Ensure data directory is included in the package
data_files = []
for root, dirs, files in os.walk("data"):
    if files:
        data_files.append((root, [os.path.join(root, f) for f in files]))

setup(
    name="fortipass",
    version="1.0.0",
    description="Professional Password Strength Visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FortiPass Team",
    author_email="info@fortipass.example.com",
    url="https://github.com/fortipass/fortipass",
    packages=find_packages(),
    data_files=data_files,
    include_package_data=True,
    install_requires=[
        "PyQt5>=5.15.0",
        "reportlab>=3.6.0",
    ],
    entry_points={
        "console_scripts": [
            "fortipass=fortipass.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
) 