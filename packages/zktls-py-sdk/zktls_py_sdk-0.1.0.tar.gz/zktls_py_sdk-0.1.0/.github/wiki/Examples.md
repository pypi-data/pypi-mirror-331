# Examples

## Basic Usage

### Simple Attestation
```python
import asyncio
from zktls import NodeWrapper

async def basic_example():
    wrapper = NodeWrapper()
    try:
        # Initialize
        await wrapper.init("app_id", "app_secret")
        
        # Create request
        request = {
            "url": "https://api.example.com/data",
            "method": "GET",
            "header": {
                "Authorization": "Bearer token",
                "Content-Type": "application/json"
            },
            "body": ""
        }
        
        # Get attestation
        attestation = await wrapper.start_attestation(request)
        print(f"Received attestation for: {attestation['recipient']}")
        
        # Verify
        is_valid = await wrapper.verify_attestation(attestation)
        print(f"Attestation is valid: {is_valid}")
        
    finally:
        await wrapper.close()

asyncio.run(basic_example())
```

## Advanced Usage

### Ethereum Signing
```python
from eth_account import Account
from eth_account.messages import encode_defunct

async def ethereum_signing_example():
    # Create Ethereum account
    private_key = "your_private_key"
    account = Account.from_key(private_key)
    
    wrapper = NodeWrapper()
    try:
        await wrapper.init("app_id", "app_secret")
        
        # Get attestation
        attestation = await wrapper.start_attestation(request)
        
        # Sign attestation
        encoded = await wrapper.encode_attestation(attestation)
        message = encode_defunct(text=encoded)
        signed = account.sign_message(message)
        
        # Add signature
        attestation['signatures'].append(signed.signature.hex())
        
        # Verify signed attestation
        is_valid = await wrapper.verify_attestation(attestation)
        print(f"Signed attestation is valid: {is_valid}")
        
    finally:
        await wrapper.close()
```

### Error Handling
```python
from zktls.exceptions import AttestationError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def error_handling_example():
    wrapper = NodeWrapper()
    try:
        await wrapper.init("app_id", "app_secret")
        
        try:
            attestation = await wrapper.start_attestation(request)
        except AttestationError as e:
            logger.error(f"Attestation failed: {str(e)}")
            return
            
        try:
            is_valid = await wrapper.verify_attestation(attestation)
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return
            
        logger.info(f"Attestation verified: {is_valid}")
        
    finally:
        await wrapper.close()
```

### Custom Response Parsing
```python
import json
from typing import Dict, Any

async def parse_response_example():
    wrapper = NodeWrapper()
    try:
        await wrapper.init("app_id", "app_secret")
        
        # Create request with response parsing
        request = {
            "url": "https://api.example.com/data",
            "method": "POST",
            "header": {"Content-Type": "application/json"},
            "body": json.dumps({"query": "example"})
        }
        
        # Get attestation
        attestation = await wrapper.start_attestation(request)
        
        # Parse specific fields
        try:
            data = json.loads(attestation['data'])
            parsed = {
                "timestamp": data.get("metadata", {}).get("timestamp"),
                "items": data.get("data", {}).get("items", [])
            }
            print("Parsed data:", json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print("Failed to parse response data")
            
    finally:
        await wrapper.close()
```

### Resource Management
```python
class AttestationManager:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.wrapper = None
        
    async def __aenter__(self):
        self.wrapper = NodeWrapper()
        await self.wrapper.init(self.app_id, self.app_secret)
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        if self.wrapper:
            await self.wrapper.close()
            
    async def process_request(self, request: Dict[str, Any]) -> Dict:
        return await self.wrapper.start_attestation(request)

# Usage
async def managed_example():
    async with AttestationManager("app_id", "app_secret") as manager:
        attestation = await manager.process_request(request)
        print(f"Processed attestation: {attestation['recipient']}")
```

## Testing Examples

### Mock Testing
```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_attestation():
    mock_process = Mock()
    mock_process.stdout.readline.return_value = (
        '{"result": {"recipient": "test", "signatures": []}}'
    )
    
    with patch('subprocess.Popen', return_value=mock_process):
        wrapper = NodeWrapper()
        await wrapper.init("test", "test")
        
        attestation = await wrapper.start_attestation({
            "url": "https://test.com",
            "method": "GET",
            "header": {},
            "body": ""
        })
        
        assert attestation["recipient"] == "test"
```

### Integration Testing
```python
@pytest.mark.asyncio
async def test_full_flow():
    wrapper = NodeWrapper()
    try:
        await wrapper.init("test_id", "test_secret")
        
        # Test request encoding
        request = {
            "url": "https://test.com",
            "method": "GET",
            "header": {},
            "body": ""
        }
        encoded = await wrapper.encode_request(request)
        assert isinstance(encoded, str)
        
        # Test attestation
        attestation = await wrapper.start_attestation(request)
        assert "recipient" in attestation
        
        # Test verification
        is_valid = await wrapper.verify_attestation(attestation)
        assert is_valid is True
        
    finally:
        await wrapper.close()
```
