"""Tests for the ARIA node module."""

import pytest
from aria.node import ARIANode
from aria.consent import ARIAConsent, TaskType


class TestARIANode:
    """Tests for ARIANode class."""

    def test_node_creation_default(self):
        """Test creating a node with default settings."""
        node = ARIANode()

        assert node.node_id is not None
        assert len(node.node_id) > 0
        assert node.consent is not None
        assert node.is_running is False
        assert node.tokens_earned == 0.0

    def test_node_creation_with_id(self):
        """Test creating a node with custom ID."""
        node = ARIANode(node_id="test-node-123")
        assert node.node_id == "test-node-123"

    def test_node_creation_with_consent(self):
        """Test creating a node with custom consent."""
        consent = ARIAConsent(
            cpu_percent=50,
            max_ram_mb=1024,
            task_types=[TaskType.TEXT_GENERATION]
        )
        node = ARIANode(consent=consent)

        assert node.consent.cpu_percent == 50
        assert node.consent.max_ram_mb == 1024

    def test_node_creation_with_port(self):
        """Test creating a node with custom port."""
        node = ARIANode(port=9000)
        assert node.network.port == 9000

    def test_node_has_components(self):
        """Test that node has all required components."""
        node = ARIANode(node_id="test")

        assert node.network is not None
        assert node.engine is not None
        assert node.ledger is not None
        assert node.pouw is not None
        assert node.sobriety is not None

    def test_load_model(self):
        """Test loading a model into the node."""
        node = ARIANode(node_id="test")
        shard = node.load_model(
            model_id="aria-2b-1bit",
            num_layers=8,
            hidden_dim=256,
            shard_start=0,
            shard_end=4
        )

        assert shard is not None
        assert shard.model_id == "aria-2b-1bit"
        assert shard.layer_start == 0
        assert shard.layer_end == 4

    def test_load_model_full(self):
        """Test loading a full model."""
        node = ARIANode(node_id="test")
        shard = node.load_model(
            model_id="test-model",
            num_layers=4,
            hidden_dim=128
        )

        assert shard.num_layers == 4

    def test_start_stop(self):
        """Test starting and stopping the node."""
        node = ARIANode(node_id="test")

        assert node.is_running is False

        node.start()
        assert node.is_running is True

        node.stop()
        assert node.is_running is False

    def test_process_request(self):
        """Test processing an inference request."""
        node = ARIANode(node_id="test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        result = node.process_request(
            query="What is AI?",
            model_id="aria-2b-1bit",
            max_tokens=10
        )

        assert result is not None
        assert result.model_id == "aria-2b-1bit"
        assert len(result.output_tokens) > 0
        assert result.output_text is not None

        node.stop()

    def test_process_request_updates_stats(self):
        """Test that processing updates node statistics."""
        node = ARIANode(node_id="test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        initial_tokens = node.tokens_earned
        node.process_request(
            query="Test query",
            model_id="aria-2b-1bit",
            max_tokens=5
        )

        assert node.tokens_earned > initial_tokens
        node.stop()

    def test_get_stats(self):
        """Test getting node statistics."""
        node = ARIANode(node_id="test-stats")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()
        node.process_request(
            query="Test",
            model_id="aria-2b-1bit",
            max_tokens=5
        )

        stats = node.get_stats()

        assert "node_id" in stats
        assert "is_running" in stats
        assert "tokens_earned" in stats
        assert "engine" in stats
        assert "network" in stats
        assert stats["node_id"] == "test-stats"
        assert stats["is_running"] is True

        node.stop()

    def test_calculate_reward(self):
        """Test reward calculation for inference."""
        node = ARIANode(node_id="test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        result = node.process_request(
            query="Test",
            model_id="aria-2b-1bit",
            max_tokens=5
        )

        reward = node._calculate_reward(result)
        assert reward > 0
        assert isinstance(reward, float)

        node.stop()

    def test_multiple_requests(self):
        """Test processing multiple requests."""
        node = ARIANode(node_id="test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        for i in range(3):
            result = node.process_request(
                query=f"Query {i}",
                model_id="aria-2b-1bit",
                max_tokens=5
            )
            assert result is not None

        stats = node.get_stats()
        assert stats["engine"]["total_inferences"] == 3

        node.stop()

    def test_node_with_different_cpu_percent(self):
        """Test node with different CPU allocation."""
        node = ARIANode(cpu_percent=75)
        assert node.consent.cpu_percent == 75

    def test_consent_sync_with_node_id(self):
        """Test that consent gets node ID assigned."""
        node = ARIANode(node_id="sync-test")
        assert node.consent.node_id == "sync-test"

    def test_ledger_records_inference(self):
        """Test that inference is recorded in ledger."""
        node = ARIANode(node_id="ledger-test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        node.process_request(
            query="Test for ledger",
            model_id="aria-2b-1bit",
            max_tokens=5
        )

        # Check pending records in ledger
        assert len(node.ledger.pending_records) > 0

        node.stop()

    def test_pouw_receives_proof(self):
        """Test that PoUW receives proof after inference."""
        node = ARIANode(node_id="pouw-test")
        node.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        node.start()

        node.process_request(
            query="Test for pouw",
            model_id="aria-2b-1bit",
            max_tokens=5
        )

        # Check that proof was submitted
        assert node.pouw.verified_count > 0

        node.stop()
