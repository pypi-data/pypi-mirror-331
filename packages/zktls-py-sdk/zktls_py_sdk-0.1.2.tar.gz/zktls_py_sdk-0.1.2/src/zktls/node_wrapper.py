"""Node.js wrapper for ZK TLS SDK"""
import json
import subprocess
import os
import time
from typing import Dict, Any, Optional, List

from .checks import check_runtime_environment, InstallationError, check_node_version, check_npm_version, check_sdk_installation

class NodeWrapper:
    """Wrapper for Node.js ZK TLS SDK"""

    CRED_VERSION = "1.0.5"

    def __init__(self):
        """Initialize wrapper and verify installation"""
        self.node_process = None  # Initialize node_process first
        self.app_id = None  # Store app_id for attestation conditions
        self.app_secret = None  # Store app_secret for attestation conditions
        
        # First check Node.js, npm and SDK installation
        node_ok, node_msg = check_node_version()
        if not node_ok:
            raise InstallationError(
                f"Node.js check failed: {node_msg}\n"
                "Please install Node.js 14+ from https://nodejs.org/"
            )

        npm_ok, npm_msg = check_npm_version()
        if not npm_ok:
            raise InstallationError(
                f"npm check failed: {npm_msg}\n"
                "Please install npm 6+ by updating Node.js"
            )

        sdk_ok, sdk_msg = check_sdk_installation()
        if not sdk_ok:
            raise InstallationError(
                f"SDK check failed: {sdk_msg}\n"
                "Please run: npm install @primuslabs/zktls-core-sdk"
            )
            
        # Setup environment before checking wrapper script
        self._setup_node_environment()
        
        # Now check runtime environment
        check_runtime_environment()
        
    def _setup_node_environment(self):
        """Setup Node.js environment"""
        # Create node script directory if not exists
        script_dir = os.path.join(os.getcwd(), "node_scripts")
        os.makedirs(script_dir, exist_ok=True)
        
        # Write wrapper script
        wrapper_script = """
// Ensure stdout is set to unbuffered mode
process.stdout._handle.setBlocking(true);

// Send ready signal immediately
process.stdout.write(JSON.stringify({ ready: true }) + '\\n');
process.stdout._handle.setBlocking(true);

const { PrimusCoreTLS } = require('@primuslabs/zktls-core-sdk');
const { encodeRequest, encodeResponse, encodeAttestation } = require('@primuslabs/zktls-core-sdk/dist/utils');

// Create global instance
let zkTLS = null;

// Handle errors
process.on('uncaughtException', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\\n');
    process.stdout._handle.setBlocking(true);
});

process.on('unhandledRejection', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\\n');
    process.stdout._handle.setBlocking(true);
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
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'startAttestation':
                if (!zkTLS) throw new Error('Not initialized');
                
                // Generate request params
                const attRequest = zkTLS.generateRequestParams(
                    params.request,
                    params.responseResolves || [],
                    params.userAddress
                );
                
                // Set attestation mode if provided
                if (params.attMode) {
                    attRequest.setAttMode(params.attMode);
                }
                
                // Set attestation conditions if provided
                if (params.attConditions) {
                    attRequest.setAttConditions(params.attConditions);
                    
                    // Set SSL cipher if provided in conditions
                    if (params.attConditions.sslCipher) {
                        attRequest.setSslCipher(params.attConditions.sslCipher);
                    }
                }
                
                // Set additional params if provided
                if (params.additionParams) {
                    attRequest.setAdditionParams(params.additionParams);
                }
                
                const attestation = await zkTLS.startAttestation(attRequest);
                process.stdout.write(JSON.stringify({ result: attestation }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'verifyAttestation':
                if (!zkTLS) throw new Error('Not initialized');
                const verified = zkTLS.verifyAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: verified }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeRequest':
                const encodedRequest = encodeRequest(params.request);
                process.stdout.write(JSON.stringify({ result: encodedRequest }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeResponse':
                const encodedResponse = encodeResponse(params.response);
                process.stdout.write(JSON.stringify({ result: encodedResponse }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeAttestation':
                const encodedAttestation = encodeAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: encodedAttestation }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'healthCheck':
                process.stdout.write(JSON.stringify({ result: true }) + '\\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            default:
                throw new Error(`Unknown method: ${method}`);
        }
    } catch (error) {
        process.stdout.write(JSON.stringify({ 
            error: error.message,
            stack: error.stack
        }) + '\\n');
        process.stdout._handle.setBlocking(true);
    }
});
"""
        with open(os.path.join(script_dir, "wrapper.js"), "w") as f:
            f.write(wrapper_script)
            
    async def _start_node_process(self):
        """Start Node.js process"""
        if not self.node_process or self.node_process.poll() is not None:
            try:
                script_dir = os.path.join(os.getcwd(), "node_scripts")
                self.node_process = subprocess.Popen(
                    ["node", os.path.join(script_dir, "wrapper.js")],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1  # Line buffered
                )
                
                # Wait for ready signal
                ready_signal = json.loads(self.node_process.stdout.readline())
                if not ready_signal.get("ready"):
                    stderr = self.node_process.stderr.read()
                    raise RuntimeError(f"Node.js process failed to start: {stderr}")
                
                # Perform health check
                health_check = await self._send_command("healthCheck", {}, skip_start=True)
                if not health_check:
                    raise RuntimeError("Node.js process health check failed")
                    
            except Exception as e:
                stderr = ""
                if self.node_process:
                    stderr = self.node_process.stderr.read()
                    self.node_process.terminate()
                    self.node_process = None
                raise RuntimeError(f"Failed to start Node.js process: {str(e)}\nstderr: {stderr}")
            
    async def _send_command(self, method: str, params: Dict[str, Any], skip_start: bool = False) -> Any:
        """Send command to Node.js process"""
        if not skip_start:
            await self._start_node_process()
            
        try:
            # Send command
            command = json.dumps({"method": method, "params": params}) + "\n"
            self.node_process.stdin.write(command)
            self.node_process.stdin.flush()
            
            # Read response
            response = json.loads(self.node_process.stdout.readline())
            
            if "error" in response:
                if "stack" in response:
                    raise RuntimeError(f"{response['error']}\nStack: {response['stack']}")
                raise RuntimeError(response["error"])
                
            return response["result"]
            
        except Exception as e:
            # Kill process on error
            if self.node_process:
                self.node_process.terminate()
                self.node_process = None
            raise RuntimeError(f"Command failed: {str(e)}")
            
    async def init(self, app_id: str, app_secret: str) -> Dict[str, Any]:
        """Initialize the SDK"""
        self.app_id = app_id
        self.app_secret = app_secret
        return await self._send_command("init", {
            "appId": app_id,
            "appSecret": app_secret
        })
        
    async def encode_request(self, request: Dict[str, Any]) -> str:
        """Encode request data"""
        return await self._send_command("encodeRequest", {"request": request})
        
    async def encode_response(self, response: Dict[str, Any]) -> str:
        """Encode response data"""
        return await self._send_command("encodeResponse", {"response": response})
        
    async def encode_attestation(self, attestation: Dict[str, Any]) -> str:
        """Encode attestation data"""
        return await self._send_command("encodeAttestation", {"attestation": attestation})
        
    def _get_default_conditions(self, request: Dict[str, Any], user_address: str, template_id: str) -> Dict[str, Any]:
        """Get default attestation conditions"""
        if not self.app_id or not self.app_secret:
            raise RuntimeError("SDK not initialized. Call init() first.")
            
        # Extract host from URL
        from urllib.parse import urlparse
        host = urlparse(request["url"]).netloc
        
        return {
            "source": "source",
            "requestid": f"test-{int(time.time())}",
            "padoUrl": "wss://api-dev.padolabs.org/algorithm-proxyV2",
            "proxyUrl": "wss://api-dev.padolabs.org/algoproxyV2",
            "basePort": "443",
            "getdatatime": str(int(time.time() * 1000)),
            "credVersion": self.CRED_VERSION,
            "modelType": "proxytls",
            "user": {
                "userid": "test-user",
                "address": user_address,
                "token": "test-token"
            },
            "authUseridHash": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            "appParameters": {
                "appId": self.app_id,
                "appSignParameters": "{}",
                "appSignature": self.app_secret,
                "additionParams": ""
            },
            "reqType": "web",
            "host": host,
            "templateId": template_id,
            "PADOSERVERURL": "https://api-dev.padolabs.org",
            "padoExtensionVersion": "0.3.19",
            "sslCipher": "ECDHE-ECDSA-AES128-GCM-SHA256"
        }
        
    async def start_attestation(
        self,
        request: Dict[str, Any],
        response_resolves: List[Dict[str, Any]],
        user_address: str = "0x0000000000000000000000000000000000000000",
        att_mode: Optional[Dict[str, Any]] = None,
        att_conditions: Optional[Dict[str, Any]] = None,
        addition_params: Optional[Dict[str, Any]] = None,
        template_id: str = "test-template"
    ) -> Dict[str, Any]:
        """Start attestation process"""
        # Set default attestation mode if not provided
        if att_mode is None:
            att_mode = {
                "algorithmType": "proxytls",
                "resultType": "web"
            }
            
        # Get default conditions and merge with provided conditions
        default_conditions = self._get_default_conditions(request, user_address, template_id)
        if att_conditions:
            default_conditions.update(att_conditions)
            
        return await self._send_command("startAttestation", {
            "request": request,
            "responseResolves": response_resolves,
            "userAddress": user_address,
            "attMode": att_mode,
            "attConditions": default_conditions,
            "additionParams": addition_params
        })
        
    async def verify_attestation(self, attestation: Dict[str, Any]) -> bool:
        """Verify attestation"""
        return await self._send_command("verifyAttestation", {"attestation": attestation})
        
    def __del__(self):
        """Cleanup Node.js process"""
        if self.node_process:
            self.node_process.terminate()
            self.node_process = None
    
