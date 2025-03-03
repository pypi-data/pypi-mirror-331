# Troubleshooting Guide

## Common Issues

### Installation Issues

#### Node.js Not Found
```
Error: Node.js executable not found in PATH
```

**Solution:**
1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Verify installation:
   ```bash
   node --version
   npm --version
   ```
3. Ensure Node.js is in PATH
4. Restart your terminal/IDE

#### Core SDK Not Found
```
Error: Cannot find module '@primuslabs/zktls-core-sdk'
```

**Solution:**
1. Install the core SDK:
   ```bash
   npm install @primuslabs/zktls-core-sdk
   ```
2. Verify installation:
   ```bash
   npm list | grep zktls-core-sdk
   ```

#### Python Dependencies
```
Error: No module named 'zktls'
```

**Solution:**
1. Install the package:
   ```bash
   pip install zktls-py-sdk
   ```
2. Check virtual environment:
   ```bash
   pip list | grep zktls
   ```

### Runtime Issues

#### Node.js Process Error
```
Error: Failed to start Node.js process
```

**Solution:**
1. Check Node.js installation
2. Verify permissions
3. Check system resources
4. Look for conflicting processes

#### Attestation Errors

1. **Invalid Request Format**
   ```
   Error: Invalid request format
   ```
   Solution: Verify request object structure:
   ```python
   request = {
       "url": "https://example.com",
       "method": "GET",
       "header": {},
       "body": ""
   }
   ```

2. **Signature Verification Failed**
   ```
   Error: Invalid signature
   ```
   Solution: Check Ethereum account and signing:
   ```python
   # Verify account
   print(f"Using address: {account.address}")
   
   # Check signature format
   print(f"Signature: {signed.signature.hex()}")
   ```

3. **Connection Issues**
   ```
   Error: Failed to connect to attestation service
   ```
   Solution: Check network and credentials:
   ```python
   # Test connection
   import aiohttp
   async with aiohttp.ClientSession() as session:
       async with session.get(url) as response:
           print(f"Status: {response.status}")
   ```

### Performance Issues

#### Memory Usage
If the Node.js process uses too much memory:

1. Clean up resources:
   ```python
   await wrapper.close()
   ```

2. Use context manager:
   ```python
   async with NodeWrapper() as wrapper:
       # Use wrapper
   ```

#### Slow Response Times
If attestations are slow:

1. Check network connection
2. Monitor Node.js process:
   ```python
   import psutil
   
   def check_node_process(pid):
       process = psutil.Process(pid)
       print(f"CPU Usage: {process.cpu_percent()}%")
       print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")
   ```

## Debugging

### Enable Debug Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('zktls')
```

### Check Node.js Output
```python
import subprocess

process = subprocess.Popen(
    ['node', '--version'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
stdout, stderr = process.communicate()
print(f"Node.js output: {stdout.decode()}")
print(f"Errors: {stderr.decode()}")
```

### Test Installation
```python
async def test_setup():
    wrapper = NodeWrapper()
    try:
        # Test Node.js
        node_version = subprocess.check_output(
            ['node', '--version']
        ).decode().strip()
        print(f"Node.js version: {node_version}")
        
        # Test npm
        npm_version = subprocess.check_output(
            ['npm', '--version']
        ).decode().strip()
        print(f"npm version: {npm_version}")
        
        # Test SDK
        await wrapper.init("test", "test")
        print("SDK initialization successful")
        
    except Exception as e:
        print(f"Setup test failed: {str(e)}")
    finally:
        await wrapper.close()
```

## Getting Help

If you're still experiencing issues:

1. **Check Documentation**
   - [Installation Guide](Installation)
   - [API Reference](API-Reference)
   - [Examples](Examples)

2. **Search Issues**
   - [Existing Issues](https://github.com/pkjha527/zktls-py-sdk/issues)
   - [Closed Issues](https://github.com/pkjha527/zktls-py-sdk/issues?q=is%3Aissue+is%3Aclosed)

3. **Create Issue**
   - Use issue templates
   - Include error messages
   - Provide system information
   - Share minimal reproduction code

4. **Community Support**
   - [Discussions](https://github.com/pkjha527/zktls-py-sdk/discussions)
   - Stack Overflow tag: `zktls-py-sdk`
