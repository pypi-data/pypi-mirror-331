# API Reference

## NodeWrapper Class

The main interface for interacting with the ZK TLS protocol.

### Constructor

```python
wrapper = NodeWrapper()
```

### Methods

#### init
```python
async def init(self, app_id: str, app_secret: str) -> bool
```
Initialize the SDK with your application credentials.

**Parameters:**
- `app_id`: Your application ID
- `app_secret`: Your application secret

**Returns:**
- `bool`: True if initialization successful

---

#### start_attestation
```python
async def start_attestation(self, request: Dict) -> Dict
```
Start an attestation process for a request.

**Parameters:**
- `request`: Dictionary containing:
  - `url`: Target URL
  - `method`: HTTP method
  - `header`: Request headers
  - `body`: Request body

**Returns:**
- `Dict`: Attestation object

---

#### encode_request
```python
async def encode_request(self, request: Dict) -> str
```
Encode a request for attestation.

**Parameters:**
- `request`: Request dictionary

**Returns:**
- `str`: Encoded request hash

---

#### encode_response
```python
async def encode_response(self, response: List[Dict]) -> str
```
Encode a response for attestation.

**Parameters:**
- `response`: List of response objects

**Returns:**
- `str`: Encoded response hash

---

#### encode_attestation
```python
async def encode_attestation(self, attestation: Dict) -> str
```
Encode an attestation for verification.

**Parameters:**
- `attestation`: Attestation object

**Returns:**
- `str`: Encoded attestation hash

---

#### verify_attestation
```python
async def verify_attestation(self, attestation: Dict) -> bool
```
Verify an attestation's validity.

**Parameters:**
- `attestation`: Attestation object

**Returns:**
- `bool`: True if attestation is valid

---

#### close
```python
async def close(self)
```
Clean up resources and close Node.js process.

## Data Types

### Request Object
```python
{
    "url": str,
    "method": str,
    "header": Dict[str, str],
    "body": str
}
```

### Attestation Object
```python
{
    "recipient": str,
    "request": Dict,
    "reponseResolve": List[Dict],
    "data": str,
    "attConditions": Dict,
    "timestamp": int,
    "additionParams": str,
    "attestors": List[str],
    "signatures": List[str]
}
```

### Response Resolve Object
```python
{
    "keyName": str,
    "parseType": str,
    "parsePath": str
}
```

## Error Handling

The SDK defines several exception types:

### AttestationError
Raised when there's an error in the attestation process.

### NodeError
Raised when there's an error in Node.js communication.

### InstallationError
Raised when there's an issue with Node.js or SDK installation.

## Best Practices

1. **Resource Management**:
   ```python
   async with NodeWrapper() as wrapper:
       await wrapper.init(app_id, app_secret)
       # Use wrapper...
   ```

2. **Error Handling**:
   ```python
   try:
       attestation = await wrapper.start_attestation(request)
   except Exception as e:
       logger.error(f"Error: {str(e)}")
   finally:
       await wrapper.close()
   ```

3. **Type Safety**:
   ```python
   from typing import Dict, List
   
   async def process_request(request: Dict) -> str:
       wrapper = NodeWrapper()
       try:
           return await wrapper.encode_request(request)
       finally:
           await wrapper.close()
   ```
