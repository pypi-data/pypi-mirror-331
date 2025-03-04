
// Ensure stdout is set to unbuffered mode
process.stdout._handle.setBlocking(true);

// Send ready signal immediately
process.stdout.write(JSON.stringify({ ready: true }) + '\n');
process.stdout._handle.setBlocking(true);

const { PrimusCoreTLS } = require('@primuslabs/zktls-core-sdk');
const { encodeRequest, encodeResponse, encodeAttestation } = require('@primuslabs/zktls-core-sdk/dist/utils');

// Create global instance
let zkTLS = null;

// Handle errors
process.on('uncaughtException', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\n');
    process.stdout._handle.setBlocking(true);
});

process.on('unhandledRejection', (error) => {
    process.stdout.write(JSON.stringify({ error: error.message }) + '\n');
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
                process.stdout.write(JSON.stringify({ result: initResult }) + '\n');
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
                process.stdout.write(JSON.stringify({ result: attestation }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'verifyAttestation':
                if (!zkTLS) throw new Error('Not initialized');
                const verified = zkTLS.verifyAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: verified }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeRequest':
                const encodedRequest = encodeRequest(params.request);
                process.stdout.write(JSON.stringify({ result: encodedRequest }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeResponse':
                const encodedResponse = encodeResponse(params.response);
                process.stdout.write(JSON.stringify({ result: encodedResponse }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'encodeAttestation':
                const encodedAttestation = encodeAttestation(params.attestation);
                process.stdout.write(JSON.stringify({ result: encodedAttestation }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            case 'healthCheck':
                process.stdout.write(JSON.stringify({ result: true }) + '\n');
                process.stdout._handle.setBlocking(true);
                break;
                
            default:
                throw new Error(`Unknown method: ${method}`);
        }
    } catch (error) {
        process.stdout.write(JSON.stringify({ 
            error: error.message,
            stack: error.stack
        }) + '\n');
        process.stdout._handle.setBlocking(true);
    }
});
