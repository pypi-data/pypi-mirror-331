# Getting Started

## Quick Start

### 1. Installation
```bash
pip install zktls-py-sdk
```

### 2. Basic Usage
```python
import asyncio
from zktls import NodeWrapper

async def main():
    wrapper = NodeWrapper()
    try:
        # Initialize
        await wrapper.init("your_app_id", "your_app_secret")
        
        # Create request
        request = {
            "url": "https://api.example.com/data",
            "method": "GET",
            "header": {"Content-Type": "application/json"},
            "body": ""
        }
        
        # Get attestation
        attestation = await wrapper.start_attestation(request)
        print(f"Attestation received: {attestation['recipient']}")
        
    finally:
        await wrapper.close()

asyncio.run(main())
```

## Core Concepts

### 1. Node Wrapper
The `NodeWrapper` class manages communication with the Node.js SDK:
- Initializes Node.js process
- Handles request/response encoding
- Manages attestation lifecycle

### 2. Attestation Flow
1. Create request object
2. Start attestation
3. Receive attestation response
4. Verify attestation
5. (Optional) Sign with Ethereum key

### 3. Request Format
```python
request = {
    "url": str,        # Target URL
    "method": str,     # HTTP method
    "header": dict,    # Request headers
    "body": str        # Request body (optional)
}
```

### 4. Attestation Object
```python
attestation = {
    "recipient": str,          # Recipient address
    "request": dict,           # Original request
    "data": str,              # Response data
    "timestamp": int,         # Unix timestamp
    "signatures": list[str]   # Attestation signatures
}
```

## Best Practices

### 1. Resource Management
```python
async with NodeWrapper() as wrapper:
    await wrapper.init(app_id, app_secret)
    # Use wrapper...
```

### 2. Error Handling
```python
from zktls.exceptions import AttestationError

try:
    attestation = await wrapper.start_attestation(request)
except AttestationError as e:
    print(f"Attestation failed: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

### 3. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting attestation...")
attestation = await wrapper.start_attestation(request)
logger.info(f"Attestation received: {attestation['recipient']}")
```

## Advanced Usage

### 1. Ethereum Integration
```python
from eth_account import Account
from eth_account.messages import encode_defunct

# Create account
private_key = "your_private_key"
account = Account.from_key(private_key)

# Sign attestation
encoded = await wrapper.encode_attestation(attestation)
message = encode_defunct(text=encoded)
signed = account.sign_message(message)

# Add signature
attestation['signatures'].append(signed.signature.hex())
```

### 2. Custom Response Parsing
```python
import json

# Parse response data
data = json.loads(attestation['data'])
result = {
    "timestamp": data["timestamp"],
    "value": data["result"]["value"]
}
```

### 3. Batch Processing
```python
async def process_batch(requests):
    async with NodeWrapper() as wrapper:
        await wrapper.init(app_id, app_secret)
        
        results = []
        for request in requests:
            try:
                attestation = await wrapper.start_attestation(request)
                results.append(attestation)
            except Exception as e:
                logger.error(f"Failed to process request: {str(e)}")
                
        return results
```

## Next Steps

1. Check out the [Examples](Examples) for more use cases
2. Read the [API Reference](API-Reference) for detailed documentation
3. Visit [Troubleshooting](Troubleshooting) if you encounter issues
4. Join our [community discussions](https://github.com/pkjha527/zktls-py-sdk/discussions)
