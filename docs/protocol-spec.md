# ARIA Protocol Specification

Technical specification for ARIA Protocol v0.2.5 WebSocket communication layer.

## Table of Contents

1. [Overview](#overview)
2. [Transport Layer](#transport-layer)
3. [Message Format](#message-format)
4. [Handshake Protocol](#handshake-protocol)
5. [Message Types](#message-types)
6. [Error Handling](#error-handling)
7. [Protocol Versioning](#protocol-versioning)
8. [Security Considerations](#security-considerations)

---

## Overview

ARIA Protocol uses WebSocket connections for real-time, bidirectional communication between nodes. The protocol operates over both `ws://` (development) and `wss://` (production) schemes.

### Design Principles

1. **Simplicity**: JSON-based messages for easy debugging
2. **Extensibility**: Version-aware message handling
3. **Resilience**: Automatic reconnection and heartbeat
4. **Security**: TLS support and message authentication

### Protocol Stack

```
┌─────────────────────────────────────┐
│          Application Layer          │
│  (Inference, Ledger, Consensus)     │
├─────────────────────────────────────┤
│          Message Layer              │
│  (JSON messages, type routing)      │
├─────────────────────────────────────┤
│          Transport Layer            │
│  (WebSocket with ping/pong)         │
├─────────────────────────────────────┤
│          Security Layer             │
│  (TLS 1.2+ for wss://)              │
└─────────────────────────────────────┘
```

---

## Transport Layer

### Connection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Protocol | WebSocket (RFC 6455) | Bidirectional communication |
| Default Port | 8765 | Configurable via CLI |
| Ping Interval | 20 seconds | Keep-alive mechanism |
| Ping Timeout | 30 seconds | Connection considered dead |
| Reconnect Delay | 5 seconds | Initial backoff |
| Max Message Size | 16 MB | For large activations |

### Connection URI Format

```
# Development (insecure)
ws://<host>:<port>

# Production (TLS)
wss://<host>:<port>

# Examples
ws://localhost:8765
wss://node.aria-protocol.org:8765
```

### WebSocket Subprotocol

The ARIA protocol uses the subprotocol identifier `aria.v0` for version negotiation:

```
GET /ws HTTP/1.1
Host: localhost:8765
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: aria.v0
```

---

## Message Format

All messages are JSON objects with a standard envelope structure.

### Base Message Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "sender_id", "data", "timestamp", "protocol"],
  "properties": {
    "type": {
      "type": "string",
      "description": "Message type identifier",
      "enum": [
        "ping", "pong",
        "peer_announce", "shard_announce",
        "get_peers",
        "inference_request", "inference_response",
        "pipeline_forward", "pipeline_result",
        "get_stats", "get_ledger_stats", "verify_ledger"
      ]
    },
    "sender_id": {
      "type": "string",
      "description": "Unique identifier of the sending node",
      "pattern": "^[a-zA-Z0-9_-]+$"
    },
    "data": {
      "type": "object",
      "description": "Message-specific payload"
    },
    "timestamp": {
      "type": "number",
      "description": "Unix timestamp (seconds since epoch)"
    },
    "protocol": {
      "type": "string",
      "description": "Protocol version string",
      "pattern": "^aria/[0-9]+\\.[0-9]+$"
    },
    "request_id": {
      "type": "string",
      "description": "Optional correlation ID for request-response pairs"
    }
  }
}
```

### Example Message

```json
{
  "type": "inference_request",
  "sender_id": "node-abc123",
  "data": {
    "query": "What is machine learning?",
    "model_id": "aria-2b-1bit",
    "max_tokens": 100
  },
  "timestamp": 1706745600.123,
  "protocol": "aria/0.1",
  "request_id": "req-xyz789"
}
```

---

## Handshake Protocol

### Connection Establishment

```
┌────────┐                           ┌────────┐
│ Client │                           │ Server │
└───┬────┘                           └───┬────┘
    │                                    │
    │  1. WebSocket CONNECT              │
    │ ──────────────────────────────────►│
    │                                    │
    │  2. WebSocket ACCEPT               │
    │ ◄──────────────────────────────────│
    │                                    │
    │  3. peer_announce                  │
    │ ──────────────────────────────────►│
    │                                    │
    │  4. peer_announce_response         │
    │ ◄──────────────────────────────────│
    │                                    │
    │  5. shard_announce (optional)      │
    │ ──────────────────────────────────►│
    │                                    │
```

### Step 3: peer_announce

Sent by connecting node to introduce itself.

```json
{
  "type": "peer_announce",
  "sender_id": "node-abc123",
  "data": {
    "node_id": "node-abc123",
    "host": "192.168.1.100",
    "port": 8765,
    "consent": {
      "cpu_percent": 25,
      "max_ram_mb": 512,
      "schedule": "08:00-22:00",
      "task_types": ["text_generation", "code_generation"],
      "privacy_level": 1
    },
    "shards": ["aria-2b-1bit_L0-7", "aria-2b-1bit_L8-15"]
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

### Step 4: peer_announce_response

Server acknowledges the connection.

```json
{
  "status": "accepted",
  "peer_id": "node-server123",
  "peer_count": 5
}
```

### Rejection Scenarios

| Status | Reason | Action |
|--------|--------|--------|
| `rejected` | Protocol version mismatch | Upgrade client |
| `rejected` | Invalid consent | Fix consent parameters |
| `rejected` | Banned node | Contact network admin |
| `rate_limited` | Too many connections | Wait and retry |

---

## Message Types

### Heartbeat Messages

#### ping

Keep-alive message sent periodically.

```json
{
  "type": "ping",
  "sender_id": "node-abc123",
  "data": {
    "timestamp": 1706745600.0
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

#### pong

Response to ping message.

```json
{
  "type": "pong",
  "node_id": "node-server123",
  "timestamp": 1706745600.1,
  "peer_count": 5
}
```

---

### Peer Discovery Messages

#### get_peers

Request list of known peers.

```json
{
  "type": "get_peers",
  "sender_id": "node-abc123",
  "data": {
    "max_peers": 10,
    "filter": {
      "has_shard": "aria-2b-1bit_L0-7"
    }
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

#### get_peers_response

```json
{
  "peers": [
    {
      "node_id": "node-xyz789",
      "host": "192.168.1.101",
      "port": 8766,
      "reputation": 0.95,
      "available_shards": ["aria-2b-1bit_L0-7"],
      "total_inferences": 1234,
      "avg_latency_ms": 45.2,
      "energy_efficiency": 0.8
    }
  ]
}
```

---

### Shard Management Messages

#### shard_announce

Broadcast available model shards.

```json
{
  "type": "shard_announce",
  "sender_id": "node-abc123",
  "data": {
    "shard_ids": [
      "aria-2b-1bit_L0-7",
      "aria-2b-1bit_L8-15"
    ]
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

### Shard ID Format

```
<model_id>_L<start>-<end>

Examples:
  aria-2b-1bit_L0-7      # Layers 0-7 of aria-2b-1bit
  aria-2b-1bit_L8-15     # Layers 8-15 of aria-2b-1bit
  aria-2b-1bit_L16-23    # Layers 16-23 of aria-2b-1bit
```

---

### Inference Messages

#### inference_request

Request inference processing.

```json
{
  "type": "inference_request",
  "sender_id": "node-abc123",
  "data": {
    "request_id": "req-xyz789",
    "query": "What is machine learning?",
    "model_id": "aria-2b-1bit",
    "task_type": "text_generation",
    "max_tokens": 100,
    "temperature": 0.7,
    "ram_mb": 512,
    "reward": 0.01
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1",
  "request_id": "req-xyz789"
}
```

**Data Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| request_id | string | Yes | Unique request identifier |
| query | string | Yes | Input text to process |
| model_id | string | Yes | Model to use for inference |
| task_type | string | No | Task type (default: text_generation) |
| max_tokens | integer | No | Maximum output tokens (default: 256) |
| temperature | float | No | Sampling temperature (default: 0.7) |
| ram_mb | integer | No | RAM requirement in MB |
| reward | float | No | ARIA tokens offered |

#### inference_response

```json
{
  "status": "completed",
  "result": {
    "output": "Machine learning is a subset of artificial intelligence...",
    "tokens_generated": 87,
    "latency_ms": 234.5,
    "energy_mj": 28.3,
    "model_id": "aria-2b-1bit",
    "nodes_used": ["node-abc123"]
  }
}
```

---

### Pipeline Messages

#### pipeline_forward

Forward activations to next node in pipeline.

```json
{
  "type": "pipeline_forward",
  "sender_id": "node-abc123",
  "data": {
    "state": {
      "request_id": "req-xyz789",
      "model_id": "aria-2b-1bit",
      "current_layer": 8,
      "activations": "<base64-encoded-tensor>",
      "shape": [1, 128, 2048],
      "dtype": "float32",
      "checksum": "sha256:abcd1234..."
    },
    "is_replica": false,
    "pipeline_chain": [
      {"node_id": "node-abc123", "layers": "L0-7"},
      {"node_id": "node-xyz789", "layers": "L8-15"},
      {"node_id": "node-def456", "layers": "L16-23"}
    ],
    "stage_index": 1
  },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

**State Fields:**

| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Original request ID |
| model_id | string | Model being processed |
| current_layer | integer | Next layer to process |
| activations | string | Base64-encoded activation tensor |
| shape | array | Tensor dimensions |
| dtype | string | Data type (float32, float16) |
| checksum | string | SHA-256 of raw activations |

#### pipeline_result

Return from pipeline stage.

```json
{
  "status": "success",
  "state": {
    "request_id": "req-xyz789",
    "current_layer": 16,
    "activations": "<base64-encoded-tensor>",
    "shape": [1, 128, 2048],
    "dtype": "float32",
    "checksum": "sha256:efgh5678..."
  },
  "metrics": {
    "latency_ms": 45.2,
    "energy_mj": 8.5
  }
}
```

---

### Statistics Messages

#### get_stats

Request node statistics.

```json
{
  "type": "get_stats",
  "sender_id": "cli",
  "data": {},
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

#### get_stats_response

```json
{
  "status": "ok",
  "data": {
    "node_id": "node-abc123",
    "uptime_seconds": 3600,
    "tokens_earned": 1.234,
    "engine": {
      "total_inferences": 100,
      "total_energy_mj": 2830.0,
      "loaded_models": 1,
      "shards": ["aria-2b-1bit_L0-23"]
    },
    "network": {
      "total_peers": 5,
      "alive_peers": 4,
      "connected_peers": 3,
      "messages_sent": 1234,
      "messages_received": 1189
    }
  }
}
```

#### get_ledger_stats

Request ledger statistics.

```json
{
  "type": "get_ledger_stats",
  "sender_id": "cli",
  "data": {},
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

#### verify_ledger

Request ledger integrity verification.

```json
{
  "type": "verify_ledger",
  "sender_id": "cli",
  "data": {},
  "timestamp": 1706745600.0,
  "protocol": "aria/0.1"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "additional context"
  }
}
```

### Error Codes

| Code | HTTP Equiv | Description |
|------|------------|-------------|
| `INVALID_MESSAGE` | 400 | Malformed JSON or missing fields |
| `UNKNOWN_TYPE` | 400 | Unrecognized message type |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Action not permitted |
| `NOT_FOUND` | 404 | Resource not found |
| `TIMEOUT` | 408 | Operation timed out |
| `CONFLICT` | 409 | Resource state conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server-side error |
| `UNAVAILABLE` | 503 | Service temporarily unavailable |

### Retry Policy

| Error Code | Retry | Backoff |
|------------|-------|---------|
| `TIMEOUT` | Yes | Exponential (1s, 2s, 4s, 8s) |
| `RATE_LIMITED` | Yes | Use Retry-After if provided |
| `UNAVAILABLE` | Yes | Exponential (5s, 10s, 20s) |
| `INTERNAL_ERROR` | Maybe | Once after 5s |
| Others | No | N/A |

---

## Protocol Versioning

### Version String Format

```
aria/<major>.<minor>

Examples:
  aria/0.1   # Current development version
  aria/1.0   # Future stable release
```

### Compatibility Rules

1. **Minor version changes** are backward compatible
2. **Major version changes** may break compatibility
3. Nodes MUST include protocol version in every message
4. Nodes SHOULD support at least one previous minor version

### Version Negotiation

During handshake, nodes exchange supported versions:

```json
{
  "type": "peer_announce",
  "data": {
    "supported_protocols": ["aria/0.1", "aria/0.2"]
  },
  "protocol": "aria/0.1"
}
```

Server responds with selected version:

```json
{
  "status": "accepted",
  "selected_protocol": "aria/0.1"
}
```

---

## Security Considerations

### TLS Requirements

For `wss://` connections:

| Requirement | Value |
|-------------|-------|
| Minimum TLS Version | 1.2 |
| Recommended TLS Version | 1.3 |
| Certificate Validation | Required in production |
| Self-signed Certificates | Allowed in development |

### Message Authentication

Future versions will include message signing:

```json
{
  "type": "inference_request",
  "sender_id": "node-abc123",
  "data": { ... },
  "timestamp": 1706745600.0,
  "protocol": "aria/0.2",
  "signature": "ed25519:<base64-signature>"
}
```

### Rate Limiting

Nodes SHOULD implement rate limiting:

| Message Type | Limit |
|--------------|-------|
| ping | 1/second |
| peer_announce | 1/minute |
| inference_request | 10/second |
| pipeline_forward | 100/second |

### Timestamp Validation

- Messages with timestamps > 5 minutes in the past SHOULD be rejected
- Messages with timestamps > 1 minute in the future SHOULD be rejected
- Clock skew tolerance: 30 seconds

---

## Appendix A: JSON Schemas

Full JSON schemas for all message types are available at:
`https://github.com/aria-protocol/aria-protocol/tree/main/schemas/`

## Appendix B: Reference Implementation

The reference implementation is in `aria/network.py`:

- `ARIANetwork.create_message()` - Message creation
- `ARIANetwork.handle_message()` - Message routing
- `ARIANetwork._handle_*()` - Individual handlers

---

*Specification Version: 0.2.5*
*Last Updated: 2026-02-01*
