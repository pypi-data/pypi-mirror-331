# Quick Start Guide

## Installation

Install the ZK TLS Python SDK using pip:

```bash
pip install zktls-py-sdk
```

## Basic Usage

### 1. Initialize the SDK

```python
from zktls import NodeWrapper

# Create instance
wrapper = NodeWrapper()

# Initialize with your credentials
app_id = "your-app-id"
app_secret = "your-app-secret"
await wrapper.init(app_id, app_secret)
```

### 2. Make a Simple Attestation Request

```python
# Define your request
request = {
    "url": "https://api.example.com/data",
    "header": {"Accept": "application/json"},
    "method": "GET",
    "body": ""
}

# Define how to parse the response
response_resolves = [
    {
        "keyName": "field1",
        "parseType": "string",
        "parsePath": "$.field1"
    },
    {
        "keyName": "field2",
        "parseType": "number",
        "parsePath": "$.field2"
    }
]

# Start attestation with default parameters
attestation = await wrapper.start_attestation(
    request=request,
    response_resolves=response_resolves
)
```

### 3. Verify Attestation

```python
# Verify the attestation
is_verified = await wrapper.verify_attestation(attestation)
```

## Advanced Usage

### Custom Template ID

```python
# Use a custom template
attestation = await wrapper.start_attestation(
    request=request,
    response_resolves=response_resolves,
    template_id="my-custom-template"
)
```

### Custom User Address

```python
# Specify a custom user address
attestation = await wrapper.start_attestation(
    request=request,
    response_resolves=response_resolves,
    user_address="0xYourCustomAddress"
)
```

### Full Example with Error Handling

```python
import asyncio
from zktls import NodeWrapper

async def main():
    try:
        # Initialize SDK
        wrapper = NodeWrapper()
        await wrapper.init(app_id, app_secret)
        
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
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Response Structure

The attestation response includes:

```python
{
    "recipient": "0x...",  # User address
    "request": {
        "url": "...",
        "header": "...",
        "method": "...",
        "body": ""
    },
    "reponseResolve": [
        {
            "keyName": "...",
            "parseType": "...",
            "parsePath": "..."
        }
    ],
    "data": "...",  # JSON string of resolved data
    "attConditions": "...",  # Attestation conditions
    "timestamp": 1234567890,
    "additionParams": "...",
    "attestors": [
        {
            "attestorAddr": "0x...",
            "url": "..."
        }
    ],
    "signatures": [
        "0x..."  # Attestation signatures
    ]
}
```

## Default Configuration

The SDK includes sensible defaults:

- SSL Cipher: ECDHE-ECDSA-AES128-GCM-SHA256
- Template ID: "test-template"
- User Address: "0x0000000000000000000000000000000000000000"
- Attestation Mode: {"algorithmType": "proxytls", "resultType": "web"}

## Best Practices

1. **Error Handling**: Always wrap SDK calls in try-catch blocks
2. **Initialization**: Initialize the SDK once and reuse the instance
3. **Response Parsing**: Define precise response resolves to minimize data exposure
4. **Verification**: Always verify attestations before using the data

## Development Notes

For development and testing, you may need to disable SSL verification:

```python
import os
os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"  # For testing only!
```

⚠️ **Warning**: Never disable SSL verification in production environments.
