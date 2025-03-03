"""
Setup configuration for ZK TLS SDK
"""
from setuptools import setup, find_packages
import subprocess
import sys
import os

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip().lstrip('v')
        major_version = int(version.split('.')[0])
        if major_version < 14:
            print(f"Error: Node.js version {version} is too old. Version 14+ is required.", file=sys.stderr)
            sys.exit(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Node.js is required but not found. Please install Node.js from https://nodejs.org/", file=sys.stderr)
        sys.exit(1)

def check_npm_installed():
    """Check if npm is installed"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        major_version = int(version.split('.')[0])
        if major_version < 6:
            print(f"Error: npm version {version} is too old. Version 6+ is required.", file=sys.stderr)
            sys.exit(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: npm is required but not found. Please install npm by updating Node.js.", file=sys.stderr)
        sys.exit(1)

def install_node_dependencies():
    """Install required Node.js packages"""
    try:
        # Create package.json if it doesn't exist
        if not os.path.exists('package.json'):
            with open('package.json', 'w') as f:
                f.write('{"dependencies": {"@primuslabs/zktls-core-sdk": "^0.1.0"}}')
        
        subprocess.run(["npm", "install"], check=True)
        
        # Verify installation
        subprocess.run(
            ["node", "-e", "require('@primuslabs/zktls-core-sdk')"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing Node.js dependencies: {e}", file=sys.stderr)
        print("stdout:", e.stdout.decode() if e.stdout else "")
        print("stderr:", e.stderr.decode() if e.stderr else "")
        sys.exit(1)

# Check Node.js installation
check_node_installed()

# Check npm installation
check_npm_installed()

# Install Node.js dependencies
install_node_dependencies()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zktls-py-sdk",
    version="0.1.0",
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
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "mypy>=0.900",
            "pylint>=2.12.0",
            "pytest-mock>=3.6.0",
        ],
    },
    package_data={
        "zktls": ["node_scripts/*.js"],
    },
)
