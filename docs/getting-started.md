# Getting Started with ARIA Protocol

This guide will help you install ARIA Protocol and run your first distributed AI inference network.

## Requirements

- Python 3.10 or higher
- ~500MB disk space
- Any CPU (no GPU required!)

## Installation

### From PyPI (recommended)

```bash
pip install aria-protocol
```

### From Source

```bash
git clone https://github.com/aria-protocol/aria-protocol.git
cd aria-protocol
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/aria-protocol/aria-protocol.git
cd aria-protocol
pip install -e ".[dev]"
```

## Quick Start (3 Commands)

Get up and running in under a minute:

```bash
# 1. Start an ARIA node
aria node start --port 8765 --model aria-2b-1bit

# 2. Start the OpenAI-compatible API
aria api start --port 3000

# 3. Test inference
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "aria-2b-1bit", "messages": [{"role": "user", "content": "Hello!"}]}'
```

That's it! You now have a working ARIA node serving AI inference.

## Setting Up a Test Network (3 Nodes)

Let's create a distributed network with three nodes running pipeline parallelism.

### Terminal 1: Node Alice (Layers 0-7)

```bash
aria node start \
  --port 8765 \
  --cpu 25 \
  --schedule "00:00-23:59" \
  --model aria-2b-1bit \
  --layers 0-7
```

### Terminal 2: Node Bob (Layers 8-15)

```bash
# Start the node
aria node start \
  --port 8766 \
  --cpu 25 \
  --model aria-2b-1bit \
  --layers 8-15

# Connect to Alice
aria peers add localhost:8765
```

### Terminal 3: Node Carol (Layers 16-23)

```bash
# Start the node
aria node start \
  --port 8767 \
  --cpu 25 \
  --model aria-2b-1bit \
  --layers 16-23

# Connect to Alice and Bob
aria peers add localhost:8765
aria peers add localhost:8766
```

### Verify the Network

```bash
# Check connected peers
aria peers list

# Expected output:
# Connected Peers (2):
#   • node-abc123 @ localhost:8766 (layers 8-15)
#   • node-def456 @ localhost:8767 (layers 16-23)
```

## Running Your First Distributed Inference

### Option 1: Using the CLI

```bash
# Start API server (connects to your node)
aria api start --port 3000 --node-port 8765

# Run inference
curl -X POST http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aria-2b-1bit",
    "messages": [{"role": "user", "content": "Explain quantum computing in simple terms"}],
    "max_tokens": 100
  }'
```

### Option 2: Using Python

```python
from aria import ARIANode, ARIAConsent, TaskType

# Create consent contract
consent = ARIAConsent(
    cpu_percent=25,
    max_ram_mb=512,
    schedule="08:00-22:00",
    task_types=[TaskType.TEXT_GENERATION],
)

# Create and start node
node = ARIANode(consent=consent, port=8765)
node.load_model("aria-2b-1bit", num_layers=24)

import asyncio

async def main():
    await node.start()

    # Local inference
    result = node.process_request(
        "What is machine learning?",
        model_id="aria-2b-1bit",
        max_tokens=100
    )
    print(f"Output: {result.output}")
    print(f"Latency: {result.latency_ms}ms")
    print(f"Energy: {result.energy_mj}mJ")

    await node.stop()

asyncio.run(main())
```

### Option 3: Using OpenAI Python Client

```python
from openai import OpenAI

# Point to your local ARIA API
client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="aria"  # Any string works
)

response = client.chat.completions.create(
    model="aria-2b-1bit",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ],
    max_tokens=100
)

print(response.choices[0].message.content)
```

## Monitoring Your Node

### Start the Dashboard

```bash
aria dashboard start --port 8080 --node-port 8765
```

Open http://localhost:8080 in your browser to see:
- Real-time inference statistics
- Connected peers
- Energy consumption
- Ledger status

### Check Node Status

```bash
aria node status
```

Example output:
```
ARIA Node Status
────────────────
Node ID:     node-abc123
Port:        8765
Uptime:      2h 15m 30s
Model:       aria-2b-1bit (layers 0-23)

Statistics:
  Inferences:     142
  Tokens Earned:  0.142 ARIA
  Energy Used:    4.26 J

Network:
  Connected Peers: 2
  Messages Sent:   1,247
  Messages Recv:   1,189

Ledger:
  Chain Length:   15 blocks
  Total Records:  142
  Chain Valid:    ✓
```

### View Ledger Statistics

```bash
aria ledger stats
```

### Verify Chain Integrity

```bash
aria ledger verify
```

## Configuration Options

### Node Configuration

| Flag | Description | Default |
|------|-------------|---------|
| `--port` | WebSocket port | 8765 |
| `--cpu` | Max CPU usage (%) | 25 |
| `--ram` | Max RAM (MB) | 512 |
| `--schedule` | Available hours (UTC) | 00:00-23:59 |
| `--model` | Model to load | aria-2b-1bit |
| `--layers` | Layer range (e.g., 0-7) | all |
| `--tls` | Enable TLS/WSS encryption | disabled |
| `--cert` | Path to TLS certificate | auto-generated |
| `--key` | Path to TLS private key | auto-generated |

### API Server Configuration

| Flag | Description | Default |
|------|-------------|---------|
| `--port` | HTTP port | 3000 |
| `--node-port` | ARIA node port | 8765 |
| `--node-host` | ARIA node host | localhost |

### Dashboard Configuration

| Flag | Description | Default |
|------|-------------|---------|
| `--port` | HTTP port | 8080 |
| `--node-port` | ARIA node port | 8765 |
| `--node-host` | ARIA node host | localhost |

## TLS/WSS Secure Connections

ARIA Protocol supports TLS encryption for secure WebSocket connections (wss://).

### Quick Start with TLS

```bash
# Start a node with TLS enabled (auto-generates self-signed certificate)
aria node start --port 8765 --tls --model aria-2b-1bit
```

On first run with `--tls`, ARIA automatically generates a self-signed certificate stored in `~/.aria/tls/`.

### Using Custom Certificates

For production deployments, use your own certificates:

```bash
# With custom certificate and key
aria node start --port 8765 \
  --tls \
  --cert /path/to/server.crt \
  --key /path/to/server.key
```

### Generating Certificates

You can generate certificates using OpenSSL:

```bash
# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -newkey rsa:2048 \
  -keyout server.key -out server.crt \
  -days 365 -nodes \
  -subj "/CN=localhost"
```

Or use Let's Encrypt for production:

```bash
# Using certbot for Let's Encrypt
certbot certonly --standalone -d your-domain.com

# Use the generated certificates
aria node start --port 8765 \
  --tls \
  --cert /etc/letsencrypt/live/your-domain.com/fullchain.pem \
  --key /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### TLS with Python API

```python
from pathlib import Path
from aria import ARIANode, ARIAConsent

# Create node with TLS
node = ARIANode(
    consent=ARIAConsent(cpu_percent=25),
    port=8765,
    use_tls=True,
    # Optional: custom certificates
    cert_path=Path("/path/to/server.crt"),
    key_path=Path("/path/to/server.key"),
)

await node.start()
# Node now accepts wss:// connections
```

### Connecting to TLS-Enabled Peers

When connecting to peers with TLS enabled, ensure the client knows to use `wss://`:

```bash
# Node with TLS connecting to TLS-enabled peer
aria node start --port 8766 --tls --peers localhost:8765
```

### Security Considerations

1. **Development**: Self-signed certificates are fine for local testing
2. **Production**: Use certificates from a trusted CA (Let's Encrypt, etc.)
3. **Certificate Verification**: Disabled by default for self-signed certs
4. **Private Key Security**: Keep your private key file secure (chmod 600)

---

## Using the Demo Script

For a complete demonstration of all ARIA features:

```bash
python examples/demo.py
```

This script:
1. Creates 3 nodes with different model shards
2. Connects them in a P2P network
3. Runs local inference
4. Runs distributed pipeline inference
5. Shows provenance ledger entries
6. Displays energy savings statistics

## Troubleshooting

### Port Already in Use

```bash
# Find process using the port
lsof -i :8765

# Kill if needed
kill -9 <PID>

# Or use a different port
aria node start --port 8766
```

### Node Won't Connect to Peers

1. Check that the peer node is running:
   ```bash
   aria peers list
   ```

2. Verify network connectivity:
   ```bash
   curl http://localhost:8766
   ```

3. Check firewall settings allow WebSocket connections

### Slow Inference

1. Reduce max concurrent tasks:
   ```python
   consent = ARIAConsent(max_concurrent_tasks=1)
   ```

2. Increase CPU allocation:
   ```bash
   aria node start --cpu 50
   ```

3. Ensure model is loaded:
   ```bash
   aria node status
   ```

## Next Steps

- **[Architecture](architecture.md)** - Understand how ARIA works
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples](../examples/)** - More code examples

## Getting Help

- GitHub Issues: https://github.com/aria-protocol/aria-protocol/issues
- Documentation: https://aria-protocol.github.io/docs/

---

*Now you're ready to contribute to the distributed AI revolution!*
