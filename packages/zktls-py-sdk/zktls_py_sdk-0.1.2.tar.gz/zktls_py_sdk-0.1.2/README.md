# ZK TLS Python SDK

A Python SDK for integrating Zero-Knowledge TLS attestation into your applications.

## Overview

The ZK TLS Python SDK provides a seamless interface to the ZK TLS protocol, enabling secure and private attestation of network interactions. It wraps the Node.js ZK TLS Core SDK and provides a Pythonic interface for easy integration.

## Features

- 🔒 Secure TLS attestation
- 🔍 Response verification
- 📝 Custom templates support
- 🛠️ Configurable attestation conditions
- 🔄 Automatic SSL cipher configuration
- 🐍 Native Python async/await support

## Installation

```bash
pip install zktls-py-sdk
```

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+

The SDK will automatically check for these dependencies during initialization.

## Quick Start

```python
import asyncio
from zktls import NodeWrapper

async def main():
    # Initialize SDK
    wrapper = NodeWrapper()
    await wrapper.init("your-app-id", "your-app-secret")
    
    # Define request
    request = {
        "url": "https://api.example.com/data",
        "header": {"Accept": "application/json"},
        "method": "GET",
        "body": ""
    }
    
    # Define response resolves
    response_resolves = [
        {
            "keyName": "field1",
            "parseType": "string",
            "parsePath": "$.field1"
        }
    ]
    
    # Start attestation
    attestation = await wrapper.start_attestation(
        request=request,
        response_resolves=response_resolves
    )
    
    # Verify attestation
    is_verified = await wrapper.verify_attestation(attestation)
    print(f"Attestation verified: {is_verified}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

## Key Concepts

### Attestation Flow

1. **Initialization**: Create a NodeWrapper instance and initialize with credentials
2. **Request Definition**: Define the HTTP request and response parsing rules
3. **Attestation**: Start the attestation process with optional custom parameters
4. **Verification**: Verify the attestation response

### Response Resolves

Response resolves define how to parse and extract data from the response:

```python
response_resolves = [
    {
        "keyName": "field1",    # Name for the extracted field
        "parseType": "string",  # Expected type
        "parsePath": "$.field1" # JSONPath to the field
    }
]
```

### Templates

Templates allow customization of attestation behavior:

```python
attestation = await wrapper.start_attestation(
    request=request,
    response_resolves=response_resolves,
    template_id="my-custom-template"
)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security issues, please email security@primuslabs.xyz instead of using the issue tracker.
