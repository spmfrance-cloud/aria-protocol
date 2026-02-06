"""Tests for the ARIA OpenAI-compatible API endpoints.

Covers:
- GET /v1/models (should return 200, not 500)
- GET /v1/status
- POST /v1/chat/completions with mocked subprocess backend
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from aria.api import ARIAOpenAIServer


# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture
def server():
    """Create an ARIAOpenAIServer instance for testing."""
    return ARIAOpenAIServer(port=3099, node_host="localhost", node_port=9999)


@pytest.fixture
def app(server):
    """Get the aiohttp app from the server."""
    return server.app


# =========================================================================
# GET /v1/models
# =========================================================================


class TestListModels:
    """Tests for GET /v1/models endpoint."""

    @pytest.mark.asyncio
    async def test_models_returns_200(self, aiohttp_client, app):
        """GET /v1/models should return 200 (not 500)."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_models_returns_list_format(self, aiohttp_client, app):
        """Response should have OpenAI list format."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        data = await resp.json()
        assert data["object"] == "list"
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_models_contains_default_models(self, aiohttp_client, app):
        """Response should contain default BitNet models."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        data = await resp.json()
        model_ids = [m["id"] for m in data["data"]]
        assert "bitnet-b1.58-large" in model_ids
        assert "bitnet-b1.58-2b-4t" in model_ids
        assert "llama3-8b-1.58" in model_ids
        assert "aria-2b-1bit" in model_ids

    @pytest.mark.asyncio
    async def test_models_owned_by_aria(self, aiohttp_client, app):
        """Each model should be owned by aria-protocol."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        data = await resp.json()
        for model in data["data"]:
            assert model["owned_by"] == "aria-protocol"

    @pytest.mark.asyncio
    async def test_models_have_ready_field(self, aiohttp_client, app):
        """Each model should have a 'ready' field."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        data = await resp.json()
        for model in data["data"]:
            assert "ready" in model
            assert isinstance(model["ready"], bool)

    @pytest.mark.asyncio
    async def test_models_have_cors_headers(self, aiohttp_client, app):
        """Response should include CORS headers."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/models")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"


# =========================================================================
# GET /v1/status
# =========================================================================


class TestStatus:
    """Tests for GET /v1/status endpoint."""

    @pytest.mark.asyncio
    async def test_status_returns_200(self, aiohttp_client, app):
        """GET /v1/status should return 200."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/status")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_status_has_required_fields(self, aiohttp_client, app):
        """Status response should have all required fields."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/status")
        data = await resp.json()
        assert "backend" in data
        assert "llama_cli_available" in data
        assert "models_count" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_status_backend_value(self, aiohttp_client, app):
        """Backend should be 'native' or 'simulation'."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/status")
        data = await resp.json()
        assert data["backend"] in ("native", "simulation")

    @pytest.mark.asyncio
    async def test_status_version(self, aiohttp_client, app):
        """Version should be set."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/status")
        data = await resp.json()
        assert data["version"] == "0.5.5"

    @pytest.mark.asyncio
    async def test_status_has_cors_headers(self, aiohttp_client, app):
        """Status response should include CORS headers."""
        client = await aiohttp_client(app)
        resp = await client.get("/v1/status")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"


# =========================================================================
# POST /v1/chat/completions
# =========================================================================


class TestChatCompletions:
    """Tests for POST /v1/chat/completions endpoint."""

    @pytest.mark.asyncio
    async def test_chat_completions_invalid_json(self, aiohttp_client, app):
        """Should return 400 for invalid JSON."""
        client = await aiohttp_client(app)
        resp = await client.post(
            "/v1/chat/completions",
            data="not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_chat_completions_empty_messages(self, aiohttp_client, app):
        """Should return 400 when messages is empty."""
        client = await aiohttp_client(app)
        resp = await client.post(
            "/v1/chat/completions",
            json={"model": "aria-2b-1bit", "messages": []},
        )
        assert resp.status == 400

    @pytest.mark.asyncio
    @patch("aria.api.check_backend_status")
    @patch("aria.api.run_inference")
    async def test_chat_completions_with_subprocess(
        self, mock_run, mock_status, aiohttp_client, app
    ):
        """Should use subprocess backend when available."""
        mock_status.return_value = {"available": True, "models": []}
        mock_run.return_value = {
            "text": "Hello! I'm here to help.",
            "tokens_generated": 10,
            "tokens_per_second": 125.0,
            "energy_mj": 15.0,
            "model": "aria-2b-1bit",
            "backend": "native",
        }

        client = await aiohttp_client(app)
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "aria-2b-1bit",
                "messages": [{"role": "user", "content": "Hello!"}],
                "max_tokens": 10,
            },
        )

        assert resp.status == 200
        data = await resp.json()
        assert data["choices"][0]["message"]["content"] == "Hello! I'm here to help."
        assert data["usage"]["tokens_per_second"] == 125.0
        assert data["usage"]["energy_mj"] == 15.0
        assert data["backend"] == "native"

    @pytest.mark.asyncio
    @patch("aria.api.check_backend_status")
    @patch("aria.api.run_inference")
    async def test_chat_completions_response_format(
        self, mock_run, mock_status, aiohttp_client, app
    ):
        """Response should match OpenAI format."""
        mock_status.return_value = {"available": True, "models": []}
        mock_run.return_value = {
            "text": "Test response",
            "tokens_generated": 5,
            "tokens_per_second": 100.0,
            "energy_mj": 10.0,
            "model": "aria-2b-1bit",
            "backend": "native",
        }

        client = await aiohttp_client(app)
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "aria-2b-1bit",
                "messages": [{"role": "user", "content": "Test"}],
            },
        )

        data = await resp.json()
        assert "id" in data
        assert data["object"] == "chat.completion"
        assert "created" in data
        assert data["model"] == "aria-2b-1bit"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["finish_reason"] == "stop"
        assert "usage" in data

    @pytest.mark.asyncio
    async def test_chat_completions_has_cors_headers(self, aiohttp_client, app):
        """Response should include CORS headers."""
        client = await aiohttp_client(app)
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "aria-2b-1bit",
                "messages": [{"role": "user", "content": "test"}],
            },
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"


# =========================================================================
# CORS Preflight
# =========================================================================


class TestCORS:
    """Tests for CORS preflight handling."""

    @pytest.mark.asyncio
    async def test_options_returns_204(self, aiohttp_client, app):
        """OPTIONS request should return 204."""
        client = await aiohttp_client(app)
        resp = await client.options("/v1/chat/completions")
        assert resp.status == 204

    @pytest.mark.asyncio
    async def test_options_cors_headers(self, aiohttp_client, app):
        """OPTIONS response should include all CORS headers."""
        client = await aiohttp_client(app)
        resp = await client.options("/v1/models")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"
        assert "POST" in resp.headers.get("Access-Control-Allow-Methods", "")
        assert "GET" in resp.headers.get("Access-Control-Allow-Methods", "")


# =========================================================================
# Health Endpoint
# =========================================================================


class TestHealth:
    """Tests for GET /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_response(self, aiohttp_client, app):
        """GET /health should return a response (200 or 503)."""
        client = await aiohttp_client(app)
        resp = await client.get("/health")
        # 503 is expected when no ARIA node is running
        assert resp.status in (200, 503)

    @pytest.mark.asyncio
    async def test_health_has_status_field(self, aiohttp_client, app):
        """Health response should have status field."""
        client = await aiohttp_client(app)
        resp = await client.get("/health")
        data = await resp.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded")
