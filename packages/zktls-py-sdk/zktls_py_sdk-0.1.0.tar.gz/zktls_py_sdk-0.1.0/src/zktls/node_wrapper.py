"""Node.js wrapper for ZK TLS SDK"""
import json
import subprocess
import os
from typing import Dict, Any, Optional, List, Union

from .checks import verify_installation, check_runtime_environment, InstallationError

class NodeWrapper:
    """Wrapper for Node.js ZK TLS SDK"""
    
    def __init__(self):
        """Initialize wrapper and verify installation"""
        try:
            verify_installation()
            check_runtime_environment()
        except InstallationError as e:
            raise RuntimeError(f"ZK TLS SDK initialization failed: {str(e)}")
            
        self.node_process: Optional[subprocess.Popen] = None
        self._setup_node_environment()
        
    def _setup_node_environment(self):
        """Setup Node.js environment"""
        # Create node script directory if not exists
        os.makedirs("node_scripts", exist_ok=True)
        
        # Write wrapper script
        wrapper_script = """
const { PrimusCoreTLS } = require('@primuslabs/zktls-core-sdk');
const { encodeRequest, encodeResponse, encodeAttestation } = require('@primuslabs/zktls-core-sdk/utils');

// Create global instance
let zkTLS = null;

// Handle errors
process.on('uncaughtException', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\\n');
});

process.on('unhandledRejection', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\\n');
});

// Handle messages from Python
process.stdin.on('data', async (data) => {
    try {
        const message = JSON.parse(data.toString());
        const { method, params } = message;
        
        switch (method) {
            case 'init':
                zkTLS = new PrimusCoreTLS();
                const initResult = await zkTLS.init(params.appId, params.appSecret);
                process.stdout.write(JSON.stringify({ result: initResult }) + '\\n');
                break;
                
            case 'startAttestation':
                if (!zkTLS) throw new Error('Not initialized');
                const attestation = await zkTLS.startAttestation(params.request);
                process.stdout.write(JSON.stringify({ result: attestation }) + '\\n');
                break;
                
            case 'verifyAttestation':
                if (!zkTLS) throw new Error('Not initialized');
                const verified = zkTLS.verifyAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: verified }) + '\\n');
                break;
                
            case 'encodeRequest':
                const encodedRequest = encodeRequest(params.request);
                process.stdout.write(JSON.stringify({ result: encodedRequest }) + '\\n');
                break;
                
            case 'encodeResponse':
                const encodedResponse = encodeResponse(params.response);
                process.stdout.write(JSON.stringify({ result: encodedResponse }) + '\\n');
                break;
                
            case 'encodeAttestation':
                const encodedAttestation = encodeAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: encodedAttestation }) + '\\n');
                break;
                
            case 'healthCheck':
                process.stdout.write(JSON.stringify({ result: true }) + '\\n');
                break;
                
            default:
                throw new Error(`Unknown method: ${method}`);
        }
    } catch (error) {
        process.stdout.write(JSON.stringify({ 
            error: error.message,
            stack: error.stack
        }) + '\\n');
    }
});
"""
        with open("node_scripts/wrapper.js", "w") as f:
            f.write(wrapper_script)
            
    def _start_node_process(self):
        """Start Node.js process"""
        if not self.node_process or self.node_process.poll() is not None:
            try:
                self.node_process = subprocess.Popen(
                    ["node", "node_scripts/wrapper.js"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Perform health check
                health_check = self._send_command("healthCheck", {})
                if not health_check:
                    raise RuntimeError("Node.js process health check failed")
                    
            except Exception as e:
                if self.node_process:
                    self.node_process.terminate()
                    self.node_process = None
                raise RuntimeError(f"Failed to start Node.js process: {str(e)}")
            
    def _send_command(self, method: str, params: Dict[str, Any]) -> Any:
        """Send command to Node.js process"""
        self._start_node_process()
        
        try:
            # Send command
            command = json.dumps({"method": method, "params": params}) + "\n"
            self.node_process.stdin.write(command)
            self.node_process.stdin.flush()
            
            # Get response
            response = json.loads(self.node_process.stdout.readline())
            if "error" in response:
                error_msg = response["error"]
                if "stack" in response:
                    error_msg += f"\n{response['stack']}"
                raise Exception(error_msg)
            return response["result"]
            
        except Exception as e:
            # Restart process on error
            if self.node_process:
                self.node_process.terminate()
                self.node_process = None
            raise Exception(f"Command failed: {str(e)}")
        
    async def init(self, app_id: str, app_secret: str) -> bool:
        """Initialize ZK TLS SDK"""
        return self._send_command("init", {
            "appId": app_id,
            "appSecret": app_secret
        })
        
    async def start_attestation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Start attestation process"""
        return self._send_command("startAttestation", {
            "request": request
        })
        
    async def verify_attestation(self, attestation: Dict[str, Any]) -> bool:
        """Verify attestation"""
        return self._send_command("verifyAttestation", {
            "attestation": attestation
        })
        
    async def encode_request(self, request: Dict[str, Any]) -> str:
        """Encode network request"""
        return self._send_command("encodeRequest", {
            "request": request
        })
        
    async def encode_response(self, response: List[Dict[str, Any]]) -> str:
        """Encode network response resolve"""
        return self._send_command("encodeResponse", {
            "response": response
        })
        
    async def encode_attestation(self, attestation: Dict[str, Any]) -> str:
        """Encode attestation"""
        return self._send_command("encodeAttestation", {
            "attestation": attestation
        })
        
    def __del__(self):
        """Cleanup Node.js process"""
        if self.node_process:
            self.node_process.terminate()
            try:
                self.node_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.node_process.kill()
