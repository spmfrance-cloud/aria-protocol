# ARIA Protocol API Reference

This document describes the OpenAI-compatible HTTP API provided by ARIA Protocol.

## Overview

ARIA provides an API that is fully compatible with the OpenAI API specification. This means you can use any OpenAI client library (Python, Node.js, etc.) to interact with ARIA nodes.

**Base URL:** `http://localhost:3000/v1`

**Authentication:** Not required for local nodes (use any string as API key)

## Starting the API Server

### Using CLI

```bash
# Start API server
aria api start --port 3000 --node-port 8765

# Check status
aria api status
```

> **Note:** `aria api stop` is planned for v0.6.0. Currently, stop the API server with Ctrl+C in the terminal where it is running.

### Using Python

```python
from aria import ARIAOpenAIServer
import asyncio

server = ARIAOpenAIServer(
    port=3000,
    node_host="localhost",
    node_port=8765
)

asyncio.run(server.start())
```

---

## Endpoints

### POST /v1/chat/completions

Create a chat completion using the ARIA inference network.

#### Request

```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer <any-string>
```

**Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID (e.g., "aria-2b-1bit") |
| `messages` | array | Yes | Array of message objects |
| `max_tokens` | integer | No | Maximum tokens to generate (default: 100) |
| `temperature` | float | No | Sampling temperature 0-2 (default: 1.0) |
| `stream` | boolean | No | Enable streaming response (default: false) |
| `top_p` | float | No | Nucleus sampling (default: 1.0) |
| `n` | integer | No | Number of completions (default: 1) |
| `stop` | string/array | No | Stop sequences |

**Message Object:**

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | "system", "user", or "assistant" |
| `content` | string | Message content |

#### Example Request

```bash
curl -X POST http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer aria" \
  -d '{
    "model": "aria-2b-1bit",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is quantum computing?"}
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

#### Response

```json
{
  "id": "chatcmpl-aria-abc123",
  "object": "chat.completion",
  "created": 1706745600,
  "model": "aria-2b-1bit",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a type of computation that harnesses quantum mechanical phenomena..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 50,
    "total_tokens": 75
  },
  "system_fingerprint": "aria-v0.5.5"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique completion ID |
| `object` | string | Always "chat.completion" |
| `created` | integer | Unix timestamp |
| `model` | string | Model used for completion |
| `choices` | array | Array of completion choices |
| `choices[].index` | integer | Choice index |
| `choices[].message` | object | Generated message |
| `choices[].finish_reason` | string | "stop", "length", or "error" |
| `usage` | object | Token usage statistics |
| `usage.prompt_tokens` | integer | Input tokens |
| `usage.completion_tokens` | integer | Output tokens |
| `usage.total_tokens` | integer | Total tokens |
| `system_fingerprint` | string | API version identifier |

---

### POST /v1/chat/completions (Streaming)

Stream the completion response using Server-Sent Events (SSE).

#### Request

```bash
curl -X POST http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer aria" \
  -d '{
    "model": "aria-2b-1bit",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "max_tokens": 200,
    "stream": true
  }'
```

#### Response (SSE Stream)

```
data: {"id":"chatcmpl-aria-abc123","object":"chat.completion.chunk","created":1706745600,"model":"aria-2b-1bit","choices":[{"index":0,"delta":{"role":"assistant","content":"Once"},"finish_reason":null}]}

data: {"id":"chatcmpl-aria-abc123","object":"chat.completion.chunk","created":1706745600,"model":"aria-2b-1bit","choices":[{"index":0,"delta":{"content":" upon"},"finish_reason":null}]}

data: {"id":"chatcmpl-aria-abc123","object":"chat.completion.chunk","created":1706745600,"model":"aria-2b-1bit","choices":[{"index":0,"delta":{"content":" a"},"finish_reason":null}]}

data: {"id":"chatcmpl-aria-abc123","object":"chat.completion.chunk","created":1706745600,"model":"aria-2b-1bit","choices":[{"index":0,"delta":{"content":" time"},"finish_reason":null}]}

data: {"id":"chatcmpl-aria-abc123","object":"chat.completion.chunk","created":1706745600,"model":"aria-2b-1bit","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

### GET /v1/models

List available models on this ARIA node.

#### Request

```bash
curl http://localhost:3000/v1/models \
  -H "Authorization: Bearer aria"
```

#### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "aria-2b-1bit",
      "object": "model",
      "created": 1706745600,
      "owned_by": "aria-protocol",
      "permission": [],
      "root": "aria-2b-1bit",
      "parent": null
    }
  ]
}
```

---

### GET /v1/status

Returns backend status including whether native inference is available.

#### Request

```bash
curl http://localhost:3000/v1/status
```

#### Response

```json
{
  "backend": "native",
  "llama_cli_available": true,
  "llama_cli_path": "/path/to/llama-cli",
  "models_count": 3,
  "version": "0.5.5"
}
```

---

### GET /v1/energy

Returns real energy consumption and savings statistics accumulated from inference requests during the current session.

#### Request

```bash
curl http://localhost:3000/v1/energy
```

#### Response

```json
{
  "session_uptime_seconds": 3600.0,
  "total_inferences": 42,
  "total_tokens_generated": 2100,
  "total_energy_mj": 1176.0,
  "total_energy_kwh": 0.000327,
  "avg_energy_per_token_mj": 0.56,
  "savings": {
    "vs_gpu": {
      "energy_saved_mj": 11812500.0,
      "energy_saved_kwh": 3.28,
      "reduction_percent": 99.99
    },
    "vs_cloud": {
      "energy_saved_mj": 14698824.0,
      "energy_saved_kwh": 4.08,
      "reduction_percent": 99.99
    },
    "co2_saved_kg": 1.64,
    "cost_saved_usd": 0.027
  },
  "recent_history": []
}
```

---

### GET /health

Check the health status of the API server and connected ARIA node.

#### Request

```bash
curl http://localhost:3000/health
```

#### Response

```json
{
  "status": "healthy",
  "version": "0.5.5",
  "uptime_seconds": 3600,
  "node": {
    "uri": "ws://localhost:8765",
    "status": "healthy",
    "node_id": "node-abc123",
    "uptime_seconds": 3600,
    "is_running": true
  },
  "endpoints": {
    "/v1/chat/completions": "available",
    "/v1/models": "available",
    "/health": "available"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "healthy" if node is reachable, "degraded" otherwise |
| `version` | string | ARIA Protocol version |
| `uptime_seconds` | integer | API server uptime |
| `node.uri` | string | WebSocket URI of the connected ARIA node |
| `node.status` | string | "healthy", "unhealthy", or "unreachable" |

Returns HTTP 200 when healthy, HTTP 503 when degraded.

---

### GET /v1/health

Alternative health endpoint (OpenAI-style path).

#### Request

```bash
curl http://localhost:3000/v1/health
```

#### Response

Same as `/health`.

---

## Using with OpenAI Client Libraries

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="aria"  # Any string works
)

# Non-streaming
response = client.chat.completions.create(
    model="aria-2b-1bit",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is ARIA Protocol?"}
    ],
    max_tokens=100
)

print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="aria-2b-1bit",
    messages=[{"role": "user", "content": "Tell me a story"}],
    max_tokens=200,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### JavaScript/Node.js

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:3000/v1',
  apiKey: 'aria',
});

async function main() {
  const completion = await client.chat.completions.create({
    model: 'aria-2b-1bit',
    messages: [
      { role: 'user', content: 'Hello!' }
    ],
    max_tokens: 100,
  });

  console.log(completion.choices[0].message.content);
}

main();
```

### cURL

```bash
# Basic request
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"aria-2b-1bit","messages":[{"role":"user","content":"Hello"}]}'

# With all options
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer aria" \
  -d '{
    "model": "aria-2b-1bit",
    "messages": [
      {"role": "system", "content": "You are a coding assistant."},
      {"role": "user", "content": "Write a Python hello world"}
    ],
    "max_tokens": 100,
    "temperature": 0.5,
    "stream": false
  }'
```

---

## Intentions API

Manage prospective memory intentions. All endpoints are local-only and require no network connectivity.

### POST /v1/intentions

Create a new intention.

**Request Body:**

```json
{
  "content": "Ask about Q4 presentation results",
  "trigger_type": "time",
  "trigger_condition": "2026-02-17T09:00:00Z",
  "priority": 0.8,
  "max_fires": 1,
  "expires_at": "2026-03-01T00:00:00Z",
  "related_topics": ["project_alpha", "quarterly_review"]
}
```

**Trigger Types:**

| Type | trigger_condition Format | Description |
|---|---|---|
| `time` | ISO 8601 datetime | Fire at or after this time |
| `semantic` | Keywords or phrase | Fire when conversation topic matches (embedding similarity > threshold) |
| `condition` | Expression string | Fire when state condition is met (e.g., "emotion=frustration") |
| `session_start` | `"*"` | Fire at the start of every new session |

**Response:** `201 Created`

```json
{
  "id": "int_a1b2c3",
  "status": "pending",
  "created_at": "2026-02-13T23:00:00Z",
  "trigger_embedding_computed": true
}
```

---

### GET /v1/intentions

List intentions with optional filters.

**Query Parameters:**

- `status` (optional): Filter by status (`pending`, `triggered`, `executed`, `expired`, `cancelled`)
- `trigger_type` (optional): Filter by trigger type
- `limit` (optional, default 20): Max results
- `sort` (optional, default `priority_desc`): Sort order

**Response:** `200 OK` — Array of intention objects.

---

### GET /v1/intentions/{id}

Get a specific intention by ID.

---

### PATCH /v1/intentions/{id}

Update an intention's properties (priority, trigger_condition, expires_at, status).

---

### DELETE /v1/intentions/{id}

Cancel and archive an intention. Sets status to `cancelled` and moves to Cold tier.

---

### POST /v1/intentions/{id}/fire

Manually trigger an intention (for testing or user-initiated reminders).

---

## Error Responses

### 400 Bad Request

Invalid request format or missing required fields.

```json
{
  "error": {
    "message": "Invalid request: 'messages' field is required",
    "type": "invalid_request_error",
    "code": "invalid_request"
  }
}
```

### 404 Not Found

Endpoint not found.

```json
{
  "error": {
    "message": "Endpoint not found",
    "type": "not_found_error",
    "code": "not_found"
  }
}
```

### 500 Internal Server Error

Server-side error during inference.

```json
{
  "error": {
    "message": "Inference failed: node connection timeout",
    "type": "server_error",
    "code": "inference_error"
  }
}
```

### 503 Service Unavailable

ARIA node is not connected or available.

```json
{
  "error": {
    "message": "ARIA node not connected",
    "type": "service_unavailable_error",
    "code": "node_unavailable"
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ARIA_API_PORT` | API server port | 3000 |
| `ARIA_NODE_HOST` | ARIA node hostname | localhost |
| `ARIA_NODE_PORT` | ARIA node port | 8765 |

### Server Options

```python
server = ARIAOpenAIServer(
    port=3000,           # HTTP server port
    node_host="localhost",  # ARIA node host
    node_port=8765,      # ARIA node WebSocket port
)
```

---

## Rate Limiting

The ARIA API does not enforce rate limits by default. Rate limiting is handled at the node level through consent contracts:

```python
consent = ARIAConsent(
    max_concurrent_tasks=2,  # Max parallel requests
    # ...
)
```

---

## CORS Support

The API server includes full CORS support for browser-based clients:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## WebSocket Protocol (Advanced)

For direct node communication, you can use the WebSocket protocol:

### Connect to Node

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  // Send inference request
  ws.send(JSON.stringify({
    type: 'inference_request',
    request_id: 'req-' + Date.now(),
    data: {
      query: 'What is AI?',
      model_id: 'aria-2b-1bit',
      max_tokens: 100
    }
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'inference_response') {
    console.log('Result:', msg.data.output);
  }
};
```

### Message Types

| Type | Description |
|------|-------------|
| `inference_request` | Request inference |
| `inference_response` | Inference result |
| `get_stats` | Request node stats |
| `stats` | Node statistics |
| `get_peers` | Request peer list |
| `peers_list` | List of connected peers |

See [Architecture](architecture.md) for full protocol documentation.

---

## Related Documentation

- **[Getting Started](getting-started.md)** - Quick start guide
- **[Architecture](architecture.md)** - System architecture and design
