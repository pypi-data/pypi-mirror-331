"""Installation and runtime checks for ZK TLS SDK"""
import os
import sys
import json
import subprocess
from typing import Tuple, Optional

class InstallationError(Exception):
    """Raised when installation requirements are not met"""
    pass

def check_node_version() -> Tuple[bool, Optional[str]]:
    """Check if Node.js is installed and meets version requirements"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip().lstrip('v')
        major_version = int(version.split('.')[0])
        if major_version < 14:
            return False, f"Node.js version {version} is too old. Version 14+ is required."
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "Node.js is not installed"

def check_npm_version() -> Tuple[bool, Optional[str]]:
    """Check if npm is installed and meets version requirements"""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        major_version = int(version.split('.')[0])
        if major_version < 6:
            return False, f"npm version {version} is too old. Version 6+ is required."
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "npm is not installed"

def check_sdk_installation() -> Tuple[bool, Optional[str]]:
    """Check if @primuslabs/zktls-core-sdk is installed"""
    try:
        # Try to require the SDK to check installation
        result = subprocess.run(
            ["node", "-e", "require('@primuslabs/zktls-core-sdk')"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "Node.js SDK is not installed correctly"
        return True, None
    except subprocess.CalledProcessError:
        return False, "Failed to check Node.js SDK installation"

def check_node_scripts() -> Tuple[bool, Optional[str]]:
    """Check if Node.js wrapper scripts are present"""
    script_path = os.path.join("node_scripts", "wrapper.js")
    if not os.path.exists(script_path):
        return False, "Node.js wrapper script is missing"
    return True, None

def verify_installation() -> None:
    """Verify all installation requirements are met"""
    # Check Node.js
    node_ok, node_msg = check_node_version()
    if not node_ok:
        raise InstallationError(
            f"Node.js check failed: {node_msg}\n"
            "Please install Node.js 14+ from https://nodejs.org/"
        )

    # Check npm
    npm_ok, npm_msg = check_npm_version()
    if not npm_ok:
        raise InstallationError(
            f"npm check failed: {npm_msg}\n"
            "Please install npm 6+ by updating Node.js"
        )

    # Check SDK installation
    sdk_ok, sdk_msg = check_sdk_installation()
    if not sdk_ok:
        raise InstallationError(
            f"SDK check failed: {sdk_msg}\n"
            "Please run: npm install @primuslabs/zktls-core-sdk"
        )

    # Check wrapper scripts
    scripts_ok, scripts_msg = check_node_scripts()
    if not scripts_ok:
        raise InstallationError(
            f"Wrapper script check failed: {scripts_msg}\n"
            "Please reinstall the package"
        )

def check_runtime_environment() -> None:
    """Check runtime environment before executing commands"""
    # Verify Node.js process can be started
    try:
        process = subprocess.Popen(
            ["node", "-e", "process.exit(0)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(timeout=5)
        if process.returncode != 0:
            raise InstallationError("Failed to start Node.js process")
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        raise InstallationError(f"Node.js process check failed: {str(e)}")

    # Verify SDK can be loaded
    try:
        process = subprocess.Popen(
            ["node", "-e", "const sdk = require('@primuslabs/zktls-core-sdk'); process.exit(0)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.wait(timeout=5)
        if process.returncode != 0:
            raise InstallationError("Failed to load Node.js SDK")
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        raise InstallationError(f"SDK load check failed: {str(e)}")

def print_environment_info() -> None:
    """Print information about the environment"""
    node_ok, node_version = check_node_version()
    npm_ok, npm_version = check_npm_version()
    
    print("\nEnvironment Information:")
    print(f"Python version: {sys.version}")
    print(f"Node.js version: {node_version if node_ok else 'Not installed'}")
    print(f"npm version: {npm_version if npm_ok else 'Not installed'}")
    
    # Get SDK version
    try:
        result = subprocess.run(
            ["npm", "list", "@primuslabs/zktls-core-sdk"],
            capture_output=True,
            text=True
        )
        print(f"SDK version: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("SDK version: Not installed")
