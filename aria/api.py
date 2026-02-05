"""
ARIA Protocol - OpenAI-Compatible API Server.

Provides a drop-in replacement for OpenAI API, allowing any tool
that uses the OpenAI API to use ARIA as a backend.

MIT License - Anthony MURGO, 2026
"""

import asyncio
import json
import time
import uuid
from typing import Optional, Dict, List, Any

from aiohttp import web
import websockets


class ARIAOpenAIServer:
    """
    OpenAI-compatible HTTP API server for ARIA Protocol.

    This server exposes endpoints that match the OpenAI API format,
    allowing any OpenAI-compatible client to use ARIA as a backend.

    Endpoints:
        POST /v1/chat/completions - Chat completions (OpenAI format)
        GET /v1/models - List available models
        GET /health - Node health status

    Example usage:
        server = ARIAOpenAIServer(port=3000, node_port=8765)
        await server.start()

    Then use with OpenAI client:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:3000/v1", api_key="aria")
        response = client.chat.completions.create(
            model="aria-2b-1bit",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """

    def __init__(self, port: int = 3000, node_host: str = "localhost",
                 node_port: int = 8765):
        """
        Initialize the OpenAI-compatible API server.

        Args:
            port: HTTP port to listen on
            node_host: ARIA node WebSocket host
            node_port: ARIA node WebSocket port
        """
        self.port = port
        self.node_host = node_host
        self.node_port = node_port
        self.node_uri = f"ws://{node_host}:{node_port}"

        self.app = web.Application()
        self._setup_routes()

        self.runner: Optional[web.AppRunner] = None
        self.is_running = False
        self.start_time: Optional[float] = None

        # Cache for models list
        self._models_cache: List[Dict] = []
        self._models_cache_time: float = 0

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_post("/v1/chat/completions", self._handle_chat_completions)
        self.app.router.add_get("/v1/models", self._handle_list_models)
        self.app.router.add_get("/health", self._handle_health)
        # Also support /v1/health for consistency
        self.app.router.add_get("/v1/health", self._handle_health)
        # CORS preflight
        self.app.router.add_options("/{path:.*}", self._handle_options)

    async def start(self):
        """Start the API server."""
        if self.is_running:
            return

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await site.start()

        self.is_running = True
        self.start_time = time.time()

        print(f"[ARIA API] OpenAI-compatible server started")
        print(f"[ARIA API] Listening on http://0.0.0.0:{self.port}")
        print(f"[ARIA API] Connected to ARIA node at {self.node_uri}")
        print(f"[ARIA API] Endpoints:")
        print(f"           POST /v1/chat/completions")
        print(f"           GET  /v1/models")
        print(f"           GET  /health")

    async def stop(self):
        """Stop the API server."""
        if not self.is_running:
            return

        if self.runner:
            await self.runner.cleanup()

        self.is_running = False
        print(f"[ARIA API] Server stopped")

    def _add_cors_headers(self, response: web.Response) -> web.Response:
        """Add CORS headers to response."""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    async def _handle_options(self, request: web.Request) -> web.Response:
        """Handle CORS preflight requests."""
        response = web.Response(status=204)
        return self._add_cors_headers(response)

    async def _send_to_node(self, msg_type: str, data: Dict) -> Optional[Dict]:
        """Send a message to the ARIA node and get response."""
        try:
            async with websockets.connect(self.node_uri, close_timeout=5) as ws:
                msg = {
                    "type": msg_type,
                    "sender_id": "api_server",
                    "data": data,
                    "timestamp": time.time(),
                    "protocol": "aria/0.1"
                }
                await ws.send(json.dumps(msg))
                response = await asyncio.wait_for(ws.recv(), timeout=60)
                return json.loads(response)
        except asyncio.TimeoutError:
            return {"error": "Request timed out"}
        except ConnectionRefusedError:
            return {"error": "Could not connect to ARIA node"}
        except Exception as e:
            return {"error": str(e)}

    async def _handle_chat_completions(self, request: web.Request) -> web.Response:
        """
        Handle POST /v1/chat/completions.

        OpenAI-compatible chat completions endpoint.
        """
        try:
            body = await request.json()
        except json.JSONDecodeError:
            response = web.json_response(
                {"error": {"message": "Invalid JSON", "type": "invalid_request_error"}},
                status=400
            )
            return self._add_cors_headers(response)

        # Extract parameters
        model = body.get("model", "aria-2b-1bit")
        messages = body.get("messages", [])
        max_tokens = body.get("max_tokens", 100)
        temperature = body.get("temperature", 0.7)
        stream = body.get("stream", False)

        if not messages:
            response = web.json_response(
                {"error": {"message": "messages is required", "type": "invalid_request_error"}},
                status=400
            )
            return self._add_cors_headers(response)

        # Convert messages to query string
        query = self._messages_to_query(messages)

        # Send inference request to ARIA node
        result = await self._send_to_node("inference_request", {
            "query": query,
            "model_id": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        })

        if not result or "error" in result:
            error_msg = result.get("error", "Unknown error") if result else "No response from node"
            response = web.json_response(
                {"error": {"message": error_msg, "type": "api_error"}},
                status=503
            )
            return self._add_cors_headers(response)

        # Handle streaming response
        if stream:
            return await self._stream_response(request, result, model)

        # Format as OpenAI response
        # The network handler returns {"status": "completed", "result": {...}}
        # where result contains the inference output from the node
        data = result.get("data", {})
        if not data:
            # Try legacy format: result directly contains the data
            data = result.get("result", {})
        output_text = data.get("output", "")
        tokens_generated = data.get("tokens_generated", data.get("tokens", 0))

        # Estimate prompt tokens (rough approximation)
        prompt_tokens = len(query.split()) * 2

        completion_id = f"aria-{uuid.uuid4().hex[:12]}"

        openai_response = {
            "id": completion_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": tokens_generated,
                "total_tokens": prompt_tokens + tokens_generated
            },
            "system_fingerprint": f"aria_{self.node_port}"
        }

        response = web.json_response(openai_response)
        return self._add_cors_headers(response)

    async def _stream_response(self, request: web.Request, result: Dict,
                               model: str) -> web.StreamResponse:
        """Handle streaming response in SSE format."""
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        await response.prepare(request)

        data = result.get("data", {})
        output_text = data.get("output", "")
        completion_id = f"aria-{uuid.uuid4().hex[:12]}"

        # Send content in chunks (simulate streaming)
        words = output_text.split()
        for i, word in enumerate(words):
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": word + (" " if i < len(words) - 1 else "")
                        },
                        "finish_reason": None
                    }
                ]
            }
            await response.write(f"data: {json.dumps(chunk)}\n\n".encode())
            await asyncio.sleep(0.01)  # Small delay for realistic streaming

        # Send final chunk
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        await response.write(f"data: {json.dumps(final_chunk)}\n\n".encode())
        await response.write(b"data: [DONE]\n\n")

        return response

    def _messages_to_query(self, messages: List[Dict]) -> str:
        """
        Convert OpenAI messages format to a query string.

        Combines all messages into a formatted prompt that preserves
        the conversation context.
        """
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")

        return "\n".join(parts)

    async def _handle_list_models(self, request: web.Request) -> web.Response:
        """
        Handle GET /v1/models.

        Returns list of available models in OpenAI format.
        """
        # Try to get models from node
        result = await self._send_to_node("get_stats", {})

        models = []
        if result and "data" in result:
            data = result.get("data", {})
            engine = data.get("engine", {})

            # Get loaded models from engine stats
            loaded_models = engine.get("loaded_models", 0)
            if loaded_models > 0:
                models.append({
                    "id": "aria-2b-1bit",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "aria-protocol",
                    "permission": [],
                    "root": "aria-2b-1bit",
                    "parent": None
                })

        # Always include default model
        if not models:
            models.append({
                "id": "aria-2b-1bit",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "aria-protocol",
                "permission": [],
                "root": "aria-2b-1bit",
                "parent": None
            })

        response = web.json_response({
            "object": "list",
            "data": models
        })
        return self._add_cors_headers(response)

    async def _handle_health(self, request: web.Request) -> web.Response:
        """
        Handle GET /health.

        Returns health status of the API server and connected node.
        """
        # Check node connection
        node_status = "unknown"
        node_info = {}

        result = await self._send_to_node("get_stats", {})
        if result and "data" in result:
            node_status = "healthy"
            data = result.get("data", {})
            node_info = {
                "node_id": data.get("node_id"),
                "uptime_seconds": data.get("uptime_seconds"),
                "is_running": data.get("is_running"),
            }
        elif result and "error" in result:
            node_status = "unhealthy"
            node_info = {"error": result["error"]}
        else:
            node_status = "unreachable"

        uptime = time.time() - self.start_time if self.start_time else 0

        health_response = {
            "status": "healthy" if node_status == "healthy" else "degraded",
            "version": "0.1.0",
            "uptime_seconds": int(uptime),
            "node": {
                "uri": self.node_uri,
                "status": node_status,
                **node_info
            },
            "endpoints": {
                "/v1/chat/completions": "available",
                "/v1/models": "available",
                "/health": "available"
            }
        }

        status_code = 200 if node_status == "healthy" else 503
        response = web.json_response(health_response, status=status_code)
        return self._add_cors_headers(response)


async def run_api_server(port: int = 3000, node_host: str = "localhost",
                         node_port: int = 8765):
    """
    Run the OpenAI-compatible API server.

    This is the main entry point for running the server standalone.

    Args:
        port: HTTP port for the API server
        node_host: ARIA node host
        node_port: ARIA node WebSocket port
    """
    server = ARIAOpenAIServer(
        port=port,
        node_host=node_host,
        node_port=node_port
    )

    await server.start()

    print("\nAPI Server is running. Press Ctrl+C to stop.\n")
    print("-" * 50)

    # Keep running
    try:
        while server.is_running:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run_api_server())
