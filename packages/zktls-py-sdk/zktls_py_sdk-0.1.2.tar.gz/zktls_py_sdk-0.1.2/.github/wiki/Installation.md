# Installation Guide

## Prerequisites

Before installing the ZK TLS Python SDK, ensure you have:

1. **Python Environment**:
   - Python 3.8 or higher
   - pip (Python package installer)
   - virtualenv (recommended)

2. **Node.js Environment**:
   - Node.js 14 or higher
   - npm (Node.js package manager)

## Installation Steps

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 2. Install Node.js Dependencies

```bash
# Install the core SDK
npm install @primuslabs/zktls-core-sdk
```

### 3. Install Python Package

#### From PyPI

```bash
pip install zktls-py-sdk
```

#### From Source

```bash
git clone https://github.com/pkjha527/zktls-py-sdk.git
cd zktls-py-sdk
pip install -e .
```

### 4. Verify Installation

```python
import asyncio
from zktls import NodeWrapper

async def verify_installation():
    wrapper = NodeWrapper()
    try:
        # This will check Node.js setup
        await wrapper.init("test", "test")
        print("Installation successful!")
    except Exception as e:
        print(f"Installation check failed: {str(e)}")
    finally:
        await wrapper.close()

asyncio.run(verify_installation())
```

## Development Installation

For development, install with additional dependencies:

```bash
pip install -e ".[dev]"
```

This includes:
- pytest for testing
- pytest-asyncio for async tests
- pytest-cov for coverage reports
- mypy for type checking

## Troubleshooting

### Common Issues

1. **Node.js Not Found**:
   ```
   Error: Node.js executable not found
   ```
   Solution: Ensure Node.js is installed and in your PATH

2. **Core SDK Not Found**:
   ```
   Error: @primuslabs/zktls-core-sdk not found
   ```
   Solution: Run `npm install @primuslabs/zktls-core-sdk`

3. **Version Conflicts**:
   ```
   Error: Incompatible Node.js version
   ```
   Solution: Upgrade Node.js to version 14 or higher

### Getting Help

If you encounter issues:
1. Check the [Troubleshooting](Troubleshooting) guide
2. Search [existing issues](https://github.com/pkjha527/zktls-py-sdk/issues)
3. Create a new issue with installation logs
