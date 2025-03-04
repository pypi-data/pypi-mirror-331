"""
Unit tests for the ZK TLS SDK Node.js wrapper.

This module contains comprehensive tests for the NodeWrapper class,
covering initialization, attestation, verification, and error handling.
"""

import os
import json
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from zktls.node_wrapper import NodeWrapper
from zktls.checks import InstallationError

# Test constants
TEST_APP_ID = os.environ.get('PRIMUS_APP_ID')
TEST_APP_SECRET = os.environ.get('PRIMUS_APP_SECRET')
TEST_URL = "https://catfact.ninja/fact"

def create_mock_process(extra_responses=None):
    """Helper to create a mock process with default responses"""
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    
    # Queue up responses for initialization and health check
    responses = [
        json.dumps({"ready": True}) + "\n",
        json.dumps({"result": True}) + "\n"  # Health check response
    ]
    
    if extra_responses:
        responses.extend(extra_responses)
        
    mock_process.stdout.readline.side_effect = responses
    return mock_process

@pytest.fixture
async def wrapper():
    """Create a NodeWrapper instance for testing."""
    os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
    wrapper = NodeWrapper()
    yield wrapper
    if wrapper.node_process:
        wrapper.node_process.terminate()

@pytest.mark.asyncio
async def test_initialization():
    """Test NodeWrapper initialization."""
    wrapper = NodeWrapper()
    assert wrapper.node_process is None
    assert wrapper.app_id is None
    assert wrapper.app_secret is None

@pytest.mark.asyncio
async def test_init_success(wrapper):
    """Test successful SDK initialization."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": True}) + "\n"  # Init response
        ])
        mock_popen.return_value = mock_process

        await wrapper.init(TEST_APP_ID, TEST_APP_SECRET)
        assert wrapper.app_id == TEST_APP_ID
        assert wrapper.app_secret == TEST_APP_SECRET

@pytest.mark.asyncio
async def test_init_failure(wrapper):
    """Test SDK initialization failure."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"error": "Init failed"}) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        with pytest.raises(RuntimeError):
            await wrapper.init("invalid_id", "invalid_secret")

@pytest.mark.asyncio
async def test_encode_request(wrapper):
    """Test request encoding."""
    request = {
        "url": TEST_URL,
        "header": {"Accept": "application/json"},
        "method": "GET",
        "body": ""
    }
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": "0x1234567890"}) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        encoded = await wrapper.encode_request(request)
        assert encoded == "0x1234567890"

@pytest.mark.asyncio
async def test_start_attestation_default_params(wrapper):
    """Test attestation with default parameters."""
    request = {
        "url": TEST_URL,
        "header": {"Accept": "application/json"},
        "method": "GET",
        "body": ""
    }
    
    response_resolves = [
        {"keyName": "fact", "parseType": "string", "parsePath": "$.fact"},
        {"keyName": "length", "parseType": "number", "parsePath": "$.length"}
    ]
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": True}) + "\n",  # Init response
            json.dumps({
                "result": {
                    "recipient": "0x0000000000000000000000000000000000000000",
                    "data": "test_data",
                    "signatures": ["0x1234"]
                }
            }) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        await wrapper.init(TEST_APP_ID, TEST_APP_SECRET)
        attestation = await wrapper.start_attestation(request, response_resolves)
        assert attestation["recipient"] == "0x0000000000000000000000000000000000000000"
        assert attestation["data"] == "test_data"
        assert attestation["signatures"] == ["0x1234"]

@pytest.mark.asyncio
async def test_start_attestation_custom_template(wrapper):
    """Test attestation with custom template."""
    request = {
        "url": TEST_URL,
        "header": {"Accept": "application/json"},
        "method": "GET",
        "body": ""
    }
    
    response_resolves = [
        {"keyName": "fact", "parseType": "string", "parsePath": "$.fact"}
    ]
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": True}) + "\n",  # Init response
            json.dumps({
                "result": {
                    "recipient": "0x0000000000000000000000000000000000000000",
                    "data": "test_data",
                    "signatures": ["0x1234"]
                }
            }) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        await wrapper.init(TEST_APP_ID, TEST_APP_SECRET)
        attestation = await wrapper.start_attestation(
            request, 
            response_resolves,
            template_id="custom-template"
        )
        assert attestation["recipient"] == "0x0000000000000000000000000000000000000000"
        assert attestation["data"] == "test_data"
        assert attestation["signatures"] == ["0x1234"]

@pytest.mark.asyncio
async def test_start_attestation_custom_user(wrapper):
    """Test attestation with custom user address."""
    request = {
        "url": TEST_URL,
        "header": {"Accept": "application/json"},
        "method": "GET",
        "body": ""
    }
    
    response_resolves = [
        {"keyName": "fact", "parseType": "string", "parsePath": "$.fact"}
    ]
    
    test_address = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": True}) + "\n",  # Init response
            json.dumps({
                "result": {
                    "recipient": test_address,
                    "data": "test_data",
                    "signatures": ["0x1234"]
                }
            }) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        await wrapper.init(TEST_APP_ID, TEST_APP_SECRET)
        attestation = await wrapper.start_attestation(
            request, 
            response_resolves,
            user_address=test_address
        )
        assert attestation["recipient"] == test_address
        assert attestation["data"] == "test_data"
        assert attestation["signatures"] == ["0x1234"]

@pytest.mark.asyncio
async def test_verify_attestation(wrapper):
    """Test attestation verification."""
    attestation = {
        "recipient": "0x0000000000000000000000000000000000000000",
        "data": "test_data",
        "signatures": ["0x1234"]
    }
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process([
            json.dumps({"result": True}) + "\n"
        ])
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        is_verified = await wrapper.verify_attestation(attestation)
        assert is_verified is True

@pytest.mark.asyncio
async def test_process_restart_on_error(wrapper):
    """Test Node.js process restart on error."""
    with patch("subprocess.Popen") as mock_popen:
        # First process fails
        failed_process = MagicMock()
        failed_process.poll.return_value = 1
        failed_process.stdout.readline.return_value = json.dumps({"ready": False}) + "\n"
        failed_process.stderr.read.return_value = "Process failed"
        
        # Second process succeeds
        success_process = create_mock_process()
        
        mock_popen.side_effect = [failed_process, success_process]
        
        # This should trigger a restart
        with pytest.raises(RuntimeError, match="Node.js process failed to start: Process failed"):
            await wrapper._start_node_process()

@pytest.mark.asyncio
async def test_cleanup():
    """Test proper cleanup of Node.js process."""
    wrapper = NodeWrapper()
    with patch("subprocess.Popen") as mock_popen:
        mock_process = create_mock_process()
        mock_popen.return_value = mock_process
        
        await wrapper._start_node_process()
        assert wrapper.node_process is not None
        
        # Cleanup
        wrapper.__del__()
        assert mock_process.terminate.called

def test_environment_check():
    """Test environment variable setting."""
    assert os.environ.get("NODE_TLS_REJECT_UNAUTHORIZED") == "0"
