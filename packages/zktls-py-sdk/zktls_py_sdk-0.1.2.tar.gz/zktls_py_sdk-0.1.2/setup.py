"""
Setup configuration for ZK TLS SDK
"""
from setuptools import setup, find_packages
import subprocess
import sys
import os
import json
from typing import List, Dict, Any

def check_node_version(min_version: str = "14.0.0") -> None:
    """Check if Node.js version meets minimum requirement"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip().lstrip('v')
        major_version = int(version.split('.')[0])
        min_major = int(min_version.split('.')[0])
        if major_version < min_major:
            sys.stderr.write(
                f"Error: Node.js version {version} is too old. Version {min_version}+ is required.\n"
                "Please upgrade Node.js: https://nodejs.org/\n"
            )
            sys.exit(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.stderr.write(
            "Error: Node.js is required but not found.\n"
            "Please install Node.js from https://nodejs.org/\n"
        )
        sys.exit(1)

def check_npm_version(min_version: str = "6.0.0") -> None:
    """Check if npm version meets minimum requirement"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        major_version = int(version.split('.')[0])
        min_major = int(min_version.split('.')[0])
        if major_version < min_major:
            sys.stderr.write(
                f"Error: npm version {version} is too old. Version {min_version}+ is required.\n"
                "Please upgrade npm: npm install -g npm@latest\n"
            )
            sys.exit(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.stderr.write(
            "Error: npm is required but not found.\n"
            "Please install npm by updating Node.js: https://nodejs.org/\n"
        )
        sys.exit(1)

def get_package_json() -> Dict[str, Any]:
    """Read and parse package.json"""
    try:
        with open('package.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        sys.stderr.write(
            "Error: package.json not found.\n"
            "This file is required for Node.js dependencies.\n"
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Invalid package.json: {e}\n")
        sys.exit(1)

def install_node_dependencies() -> None:
    """Install required Node.js packages"""
    pkg_json = get_package_json()
    
    # Get required versions from package.json
    node_version = pkg_json.get('engines', {}).get('node', '14.0.0').lstrip('>=')
    npm_version = pkg_json.get('engines', {}).get('npm', '6.0.0').lstrip('>=')
    
    # Check versions
    check_node_version(node_version)
    check_npm_version(npm_version)
    
    try:
        # Run npm install
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        
        # Run npm's postinstall script manually to verify installation
        subprocess.run(
            ["node", "-e", pkg_json['scripts']['postinstall'].strip('"')],
            check=True,
            capture_output=True
        )
        
        print("Successfully installed Node.js dependencies")
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error installing Node.js dependencies:\n")
        if e.stdout:
            sys.stderr.write(f"stdout: {e.stdout.decode()}\n")
        if e.stderr:
            sys.stderr.write(f"stderr: {e.stderr.decode()}\n")
        sys.exit(1)

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Install Node.js dependencies before setup
install_node_dependencies()

setup(
    name="zktls-py-sdk",
    version="0.1.2",
    author="Praveen Kumar Jha",
    author_email="praveen@gamp.gg",
    description="Python SDK wrapper for ZK TLS attestation service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pkjha527/zktls-py-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "eth-typing>=3.0.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "asyncio>=3.4.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "mypy>=0.900",
            "pylint>=2.12.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ],
    },
    package_data={
        "zktls": ["node_scripts/*.js"],
    },
)
