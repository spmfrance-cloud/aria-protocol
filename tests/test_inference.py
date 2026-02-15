"""Tests for the ARIA inference module."""

from aria.inference import ModelShard, InferenceResult, TernaryLayer, InferenceEngine


class TestModelShard:
    """Tests for ModelShard dataclass."""

    def test_shard_creation(self):
        """Test creating a model shard."""
        shard = ModelShard(
            shard_id="aria-2b-1bit-0-8",
            model_id="aria-2b-1bit",
            layer_start=0,
            layer_end=8,
            size_bytes=1024 * 1024,
            checksum="abc123"
        )
        assert shard.shard_id == "aria-2b-1bit-0-8"
        assert shard.model_id == "aria-2b-1bit"
        assert shard.layer_start == 0
        assert shard.layer_end == 8
        assert shard.size_bytes == 1024 * 1024

    def test_shard_num_layers(self):
        """Test num_layers property calculation."""
        shard = ModelShard(
            shard_id="test",
            model_id="test-model",
            layer_start=0,
            layer_end=8,
            size_bytes=1024,
            checksum="abc"
        )
        # num_layers = layer_end - layer_start + 1
        assert shard.num_layers == 9

    def test_shard_with_weights(self):
        """Test shard with weight data."""
        weights = b"\x00\x01\xff" * 100
        shard = ModelShard(
            shard_id="test",
            model_id="test-model",
            layer_start=0,
            layer_end=4,
            size_bytes=len(weights),
            checksum="abc",
            weights=weights
        )
        assert shard.weights is not None
        assert len(shard.weights) == 300


class TestInferenceResult:
    """Tests for InferenceResult dataclass."""

    def test_result_creation(self):
        """Test creating an inference result."""
        result = InferenceResult(
            request_id="req-123",
            output_tokens=[1, 2, 3, 4, 5],
            output_text="Hello world",
            latency_ms=150,
            energy_mj=45,
            nodes_used=["node1", "node2"],
            model_id="aria-2b-1bit",
            tokens_generated=5
        )
        assert result.request_id == "req-123"
        assert len(result.output_tokens) == 5
        assert result.output_text == "Hello world"
        assert result.latency_ms == 150
        assert result.energy_mj == 45
        assert len(result.nodes_used) == 2
        assert result.tokens_generated == 5

    def test_result_to_provenance_record(self):
        """Test converting result to provenance record."""
        result = InferenceResult(
            request_id="req-123",
            output_tokens=[1, 2, 3],
            output_text="Test output",
            latency_ms=100,
            energy_mj=50,
            nodes_used=["node1"],
            model_id="aria-2b-1bit",
            tokens_generated=3
        )
        record = result.to_provenance_record("test query")

        assert record.model_id == "aria-2b-1bit"
        assert record.latency_ms == 100
        assert record.energy_mj == 50
        assert record.tokens_generated == 3
        assert "node1" in record.node_ids


class TestTernaryLayer:
    """Tests for TernaryLayer class."""

    def test_layer_creation(self):
        """Test creating a ternary layer."""
        layer = TernaryLayer(input_dim=256, output_dim=256, layer_id=0)
        assert layer.input_dim == 256
        assert layer.output_dim == 256
        assert layer.layer_id == 0

    def test_layer_forward(self):
        """Test forward pass through ternary layer."""
        layer = TernaryLayer(input_dim=16, output_dim=16, layer_id=0)
        activations = [0.5] * 16
        output = layer.forward(activations)

        assert len(output) == 16
        assert all(isinstance(x, float) for x in output)

    def test_layer_forward_different_dims(self):
        """Test forward pass with different input/output dimensions."""
        layer = TernaryLayer(input_dim=32, output_dim=64, layer_id=0)
        activations = [0.1] * 32
        output = layer.forward(activations)

        assert len(output) == 64

    def test_layer_energy_estimate(self):
        """Test energy estimation for layer."""
        layer = TernaryLayer(input_dim=256, output_dim=256, layer_id=0)
        energy = layer.energy_estimate_mj()

        assert energy > 0
        assert isinstance(energy, float)


class TestInferenceEngine:
    """Tests for InferenceEngine class."""

    def test_engine_creation(self):
        """Test creating an inference engine."""
        engine = InferenceEngine(node_id="test-node")
        assert engine.node_id == "test-node"
        assert engine.total_inferences == 0
        assert engine.total_energy_mj == 0.0

    def test_load_model(self):
        """Test loading a model into the engine."""
        engine = InferenceEngine(node_id="test-node")
        shard = engine.load_model(
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
        """Test loading all layers of a model."""
        engine = InferenceEngine(node_id="test-node")
        shard = engine.load_model(
            model_id="test-model",
            num_layers=4,
            hidden_dim=128
        )

        assert shard.layer_start == 0
        # When shard_end is None, it becomes num_layers - 1
        assert shard.layer_end == 3

    def test_get_loaded_shard_ids(self):
        """Test getting loaded shard IDs."""
        engine = InferenceEngine(node_id="test-node")
        engine.load_model(
            model_id="aria-2b-1bit",
            num_layers=8,
            hidden_dim=256,
            shard_start=0,
            shard_end=4
        )

        shard_ids = engine.get_loaded_shard_ids()
        assert len(shard_ids) == 1
        assert "aria-2b-1bit" in shard_ids[0]

    def test_infer(self):
        """Test running inference."""
        engine = InferenceEngine(node_id="test-node")
        engine.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )

        result = engine.infer(
            query="What is AI?",
            model_id="aria-2b-1bit",
            max_tokens=10
        )

        assert result is not None
        assert isinstance(result, InferenceResult)
        assert result.model_id == "aria-2b-1bit"
        assert result.tokens_generated >= 0
        assert result.latency_ms >= 0
        assert result.energy_mj >= 0

    def test_infer_updates_stats(self):
        """Test that inference updates engine statistics."""
        engine = InferenceEngine(node_id="test-node")
        engine.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )

        initial_count = engine.total_inferences
        engine.infer(query="Test", model_id="aria-2b-1bit", max_tokens=5)

        assert engine.total_inferences == initial_count + 1
        assert engine.total_energy_mj > 0

    def test_get_stats(self):
        """Test getting engine statistics."""
        engine = InferenceEngine(node_id="test-node")
        engine.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )
        engine.infer(query="Test", model_id="aria-2b-1bit", max_tokens=5)

        stats = engine.get_stats()

        assert "node_id" in stats
        assert "total_inferences" in stats
        assert "total_energy_mj" in stats
        assert "loaded_shards" in stats
        assert stats["total_inferences"] == 1

    def test_multiple_inferences(self):
        """Test running multiple inferences."""
        engine = InferenceEngine(node_id="test-node")
        engine.load_model(
            model_id="aria-2b-1bit",
            num_layers=4,
            hidden_dim=128
        )

        for i in range(3):
            result = engine.infer(
                query=f"Query {i}",
                model_id="aria-2b-1bit",
                max_tokens=5
            )
            assert result is not None

        assert engine.total_inferences == 3
