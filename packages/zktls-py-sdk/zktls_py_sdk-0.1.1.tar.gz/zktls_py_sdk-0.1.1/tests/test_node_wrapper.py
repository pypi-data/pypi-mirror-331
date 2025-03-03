"""Tests for NodeWrapper"""
import json
import subprocess
import pytest
from unittest.mock import patch, Mock, MagicMock
from zktls.node_wrapper import NodeWrapper
from zktls.checks import InstallationError

BODY_STR = json.dumps({
    "metadata": {
        "timestamp": "2024-11-26T12:34:56Z",
        "requestId": "123e4567-e89b-12d3-a456-426614174000",
        "tags": ["large_request", "test_data", "example_usage"]
    },
    "data": {
        "items": [
            {
                "id": 1,
                "name": "Item One",
                "description": "This is a detailed description of item one.",
                "attributes": {"color": "red", "size": "large", "weight": 1.234}
            },
            {
                "id": 2,
                "name": "Item Two",
                "description": "This is a detailed description of item two.",
                "attributes": {"color": "blue", "size": "medium", "weight": 2.345}
            }
        ],
        "extraData": {
            "subField1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "subField2": ["Value1", "Value2", "Value3", "Value4"],
            "nestedField": {
                "innerField1": "Deeply nested value",
                "innerField2": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }
        }
    }
})

def create_network_request():
    """Create test network request"""
    return {
        "url": "https://example.com/apiwdewd/121s1qs1qs?DDDSADWDDAWDWAWWAWW",
        "header": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwi.M0NTY3ODM0NTY3ODM0NTY3ODM0NTY3ODM0NTY3OD..",
            "X-Custom-Header-1": "Very-Long-Custom-Header-Value-That-Exceeds-Normal-Limits-Here-1234567890l-Limits-Here-1234567l-Limits-Here-1234567l-Limits-Here-1234567l-Limits-Here-1234567l-Limits-Here-1234567...",
            "X-Custom-Header-2": "Another-Custom-Value-1234567890abcdefghijklmnopqrstuvwxyzghijklmnopqrstuvwxyghijklmnopqrstuvwxyghijklmnopqrstuvwxyghijklmnopqrstuvwxy",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MyCustomClient/1.0",
            "Cache-Control": "no-cache"
        },
        "method": "POST",
        "body": BODY_STR
    }

def create_network_response_resolve():
    """Create test network response resolve"""
    return [{
        "keyName": "dASCZCSQFEQSDCKMASODCNPOND[OJDL;AKNC;KA;LCZMOQNOQWNPWNEO2NEPIOWNEO2EQWDNLKJQBDIQNWIUNINOIEDN2ONEDOI2NEDO2ISDKSMD]ND LWHBLQBEDKJEBDIUWSILSBCLQVSCUYDUH@3344OIIOQWEJ02J0J3ajdhpohodh92njabdpuhcqnwejkbiuhc0[qwncjqnsdonqowfoqwno;9 ujdwkfpokwedm1jf[oi]wc9hce98cbuie9gd71gd87d817g219ge97129g19g2812912]",
        "parseType": "JSON121231uqwhdp9uh2i1ubdbjabdiwd1biu212",
        "parsePath": "$.data.key1kn;ni[onwendiohed2ij20djasdj09wndoiqweoqheqhefpqhf9p92hf238dhdohwuhpbfoqufp92hfo2iefinoiedn2o9302]"
    } for _ in range(3)]

def create_attestation():
    """Create test attestation"""
    return {
        "recipient": "0x7ab44DE0156925fe0c24482a2cDe48C465e47573",
        "request": create_network_request(),
        "reponseResolve": create_network_response_resolve(),
        "data": BODY_STR,
        "attConditions": {"param": "value"},
        "timestamp": 1,
        "additionParams": "",
        "attestors": [],
        "signatures": []
    }

@pytest.fixture
def mock_process():
    """Mock subprocess.Popen process"""
    process = MagicMock()
    process.poll.return_value = None
    process.stdout.readline.return_value = json.dumps({"result": True})
    process.returncode = 0
    return process

@pytest.fixture
async def wrapper(mock_process):
    """Create NodeWrapper instance"""
    # Mock installation checks
    with patch('zktls.node_wrapper.verify_installation'), \
         patch('zktls.node_wrapper.check_runtime_environment'), \
         patch('subprocess.Popen', return_value=mock_process):
        wrapper = NodeWrapper()
        yield wrapper

@pytest.mark.asyncio
async def test_encode_request(wrapper, mock_process):
    """Test encode request"""
    request = create_network_request()
    mock_process.stdout.readline.return_value = json.dumps({
        "result": "0x337e14098e0e506f44eb6fe3d46e1c0310cfdf5576f715034674a43b6b954693"
    })
    
    result = await wrapper.encode_request(request)
    assert result == "0x337e14098e0e506f44eb6fe3d46e1c0310cfdf5576f715034674a43b6b954693"

@pytest.mark.asyncio
async def test_encode_response(wrapper, mock_process):
    """Test encode response"""
    response = create_network_response_resolve()
    mock_process.stdout.readline.return_value = json.dumps({
        "result": "0xf7525104ad0472d18297fd784fa894a4e491ca2e5d4363a64adc6f4adba095e1"
    })
    
    result = await wrapper.encode_response(response)
    assert result == "0xf7525104ad0472d18297fd784fa894a4e491ca2e5d4363a64adc6f4adba095e1"

@pytest.mark.asyncio
async def test_encode_attestation(wrapper, mock_process):
    """Test encode attestation"""
    attestation = create_attestation()
    mock_process.stdout.readline.return_value = json.dumps({
        "result": "0xebb87a4b82fe5980d8e8f43fe98acda9cc44fe98541947004c648a99ff629a3f"
    })
    
    result = await wrapper.encode_attestation(attestation)
    assert result == "0xebb87a4b82fe5980d8e8f43fe98acda9cc44fe98541947004c648a99ff629a3f"

@pytest.mark.asyncio
async def test_verify_attestation(wrapper, mock_process):
    """Test verify attestation"""
    attestation = create_attestation()
    # Add signature from ethers wallet
    attestation["signatures"] = ["0x1234567890"]  # Mock signature
    
    mock_process.stdout.readline.return_value = json.dumps({
        "result": True
    })
    
    result = await wrapper.verify_attestation(attestation)
    assert result is True

@pytest.mark.asyncio
async def test_init(wrapper, mock_process):
    """Test initialization"""
    result = await wrapper.init("test_id", "test_secret")
    assert result is True

@pytest.mark.asyncio
async def test_start_attestation(wrapper, mock_process):
    """Test start attestation"""
    request = create_network_request()
    
    # Mock attestation response
    mock_process.stdout.readline.return_value = json.dumps({
        "result": create_attestation()
    })
    
    result = await wrapper.start_attestation(request)
    assert result["recipient"] == "0x7ab44DE0156925fe0c24482a2cDe48C465e47573"

@pytest.mark.asyncio
async def test_node_process_restart(wrapper, mock_process):
    """Test Node.js process restart"""
    # First call succeeds
    mock_process.stdout.readline.return_value = json.dumps({"result": True})
    result = await wrapper.init("app_id", "app_secret")
    assert result is True
    
    # Second call fails and triggers restart
    mock_process.stdout.readline.return_value = json.dumps({"error": "Process error"})
    with pytest.raises(Exception, match="Command failed: Process error"):
        await wrapper.init("app_id", "app_secret")
    
    # Verify process was restarted
    assert mock_process.terminate.called

@pytest.mark.asyncio
async def test_error_handling(wrapper, mock_process):
    """Test error handling"""
    # Test Node.js error
    mock_process.stdout.readline.return_value = json.dumps({
        "error": "Test error",
        "stack": "Error: Test error\n    at Object.<anonymous> (/test.js:1:1)"
    })
    
    with pytest.raises(Exception) as exc_info:
        await wrapper.init("app_id", "app_secret")
    
    assert "Test error" in str(exc_info.value)
    assert "at Object.<anonymous>" in str(exc_info.value)
    
    # Test process startup error
    mock_process.wait.side_effect = subprocess.TimeoutExpired(["node"], 5)
    with pytest.raises(RuntimeError, match="Failed to start Node.js process"):
        await wrapper.init("app_id", "app_secret")
