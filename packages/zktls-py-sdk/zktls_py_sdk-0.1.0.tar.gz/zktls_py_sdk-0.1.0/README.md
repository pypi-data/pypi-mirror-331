# ZK TLS Python SDK

[![PyPI version](https://badge.fury.io/py/zktls-py-sdk.svg)](https://badge.fury.io/py/zktls-py-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/zktls-py-sdk.svg)](https://pypi.org/project/zktls-py-sdk/)
[![License](https://img.shields.io/github/license/pkjha527/zktls-py-sdk.svg)](https://github.com/pkjha527/zktls-py-sdk/blob/main/LICENSE)
[![Tests](https://github.com/pkjha527/zktls-py-sdk/workflows/Tests/badge.svg)](https://github.com/pkjha527/zktls-py-sdk/actions)
[![Coverage](https://codecov.io/gh/pkjha527/zktls-py-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/pkjha527/zktls-py-sdk)

A Python SDK wrapper for Primus Labs' Zero-Knowledge TLS (ZK TLS) protocol. This SDK provides a Python interface to the official `@primuslabs/zktls-core-sdk` Node.js package, enabling secure attestation and proxy TLS functionality.

## Related SDKs

This Python SDK is built upon the official JavaScript SDK: [@primuslabs/zktls-core-sdk](https://github.com/primus-labs/zktls-js-sdk). For JavaScript or Node.js-based use cases, you can use the core SDK directly to leverage the same ZK TLS protocol capabilities.

## Features

- **✨ Zero-Knowledge Attestations**: Create and verify attestations without exposing underlying data
- **🔒 Proxy TLS**: Secure communication channel for attestation requests
- **⛓️ Ethereum Integration**: Sign requests using Ethereum private keys
- **🔄 Async Support**: Built with modern async/await patterns
- **🛡️ Type Safety**: Comprehensive type hints for reliable development
- **🔍 Health Checks**: Automatic Node.js process management and recovery
- **🚀 Performance**: Efficient subprocess communication with Node.js

## System Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- npm (usually comes with Node.js)

## Installation

### 1. Install Node.js Dependencies

First, install the required Node.js package:

```bash
npm install @primuslabs/zktls-core-sdk
```

### 2. Install Python Package

Install the Python SDK using pip:

```bash
pip install zktls-py-sdk
```

Or install from source:

```bash
git clone https://github.com/pkjha527/zktls-py-sdk.git
cd zktls-py-sdk
pip install -e .
```

## Quick Start

```python
import asyncio
from zktls import NodeWrapper

async def main():
    # Initialize wrapper
    wrapper = NodeWrapper()
    
    try:
        # Initialize with credentials
        await wrapper.init("your_app_id", "your_app_secret")
        
        # Create attestation request
        request = {
            "url": "https://api.example.com/data",
            "method": "POST",
            "header": {
                "Authorization": "Bearer your_token",
                "Content-Type": "application/json"
            },
            "body": '{"query": "example"}'
        }
        
        # Get attestation
        attestation = await wrapper.start_attestation(request)
        print(f"Received attestation for: {attestation['recipient']}")
        
        # Verify attestation
        is_valid = await wrapper.verify_attestation(attestation)
        print(f"Attestation is valid: {is_valid}")
        
    finally:
        # Clean up resources
        await wrapper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Guide

### Basic Attestation Flow

1. **Initialize the SDK**:
   ```python
   wrapper = NodeWrapper()
   await wrapper.init(app_id, app_secret)
   ```

2. **Create a Request**:
   ```python
   request = {
       "url": "https://api.example.com",
       "method": "GET",
       "header": {"Authorization": "Bearer token"},
       "body": ""
   }
   ```

3. **Get Attestation**:
   ```python
   attestation = await wrapper.start_attestation(request)
   ```

4. **Verify Attestation**:
   ```python
   is_valid = await wrapper.verify_attestation(attestation)
   ```

### Ethereum Signing Integration

```python
from eth_account import Account
from eth_account.messages import encode_defunct

# Create Ethereum account
account = Account.from_key("your_private_key")

# Get attestation
attestation = await wrapper.start_attestation(request)

# Sign attestation
encoded = await wrapper.encode_attestation(attestation)
message = encode_defunct(text=encoded)
signed = account.sign_message(message)
attestation['signatures'].append(signed.signature.hex())

# Verify signed attestation
is_valid = await wrapper.verify_attestation(attestation)
```

### Error Handling

```python
from zktls.exceptions import AttestationError

try:
    attestation = await wrapper.start_attestation(request)
    is_valid = await wrapper.verify_attestation(attestation)
except AttestationError as e:
    print(f"Attestation error: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Running Tests

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Run Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=zktls tests/
```

Run specific test file:
```bash
pytest tests/test_node_wrapper.py -v
```

### 3. Test Configuration

- Tests use pytest fixtures for mocking Node.js processes
- Async tests use pytest-asyncio
- Coverage reports are generated using pytest-cov

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://github.com/pkjha527/zktls-py-sdk/wiki)
- 🐛 [Issue Tracker](https://github.com/pkjha527/zktls-py-sdk/issues)
- 💬 [Discussions](https://github.com/pkjha527/zktls-py-sdk/discussions)

## Acknowledgments

- Primus Labs team for the core ZK TLS protocol
- Contributors to the Node.js SDK
