"""Tests for the native BitNet integration and model manager."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aria.bitnet_native import BitNetNative
from aria.model_manager import ModelManager
from aria.inference import InferenceEngine


# =============================================================================
# BitNetNative Tests
# =============================================================================


class TestBitNetNativeFallback:
    """Tests for simulation fallback when native lib is unavailable."""

    def test_fallback_to_simulation_when_lib_absent(self):
        """BitNetNative should fall back to simulation if lib not found."""
        bitnet = BitNetNative()
        assert bitnet.is_simulation is True
        assert bitnet.is_native is False
        assert bitnet.backend_name == "simulation"

    def test_simulation_mode_set_by_default(self):
        """Without a real lib, simulation mode should be the default."""
        bitnet = BitNetNative()
        assert bitnet._simulation_mode is True
        assert bitnet._lib is None

    def test_explicit_invalid_lib_path_falls_back(self):
        """Providing a non-existent lib path should fall back to simulation."""
        bitnet = BitNetNative(lib_path="/nonexistent/libbitnet.so")
        assert bitnet.is_simulation is True

    def test_repr_simulation(self):
        """Test repr in simulation mode."""
        bitnet = BitNetNative()
        r = repr(bitnet)
        assert "simulation" in r
        assert "none" in r


class TestBitNetNativeLoadModel:
    """Tests for model loading."""

    def test_load_model_simulation_mode(self):
        """Loading a model in simulation mode should succeed."""
        bitnet = BitNetNative()
        result = bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)
        assert result is True
        assert bitnet.model_loaded is True
        assert bitnet._model_name == "BitNet-b1.58-2B-4T"

    def test_load_model_unknown_raises(self):
        """Loading an unknown model should raise ValueError."""
        bitnet = BitNetNative()
        with pytest.raises(ValueError, match="Unknown model"):
            bitnet.load_model("nonexistent-model")

    def test_load_model_sets_config(self):
        """Loading a model should set the config correctly."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-large", auto_download=False)
        assert bitnet._config is not None
        assert bitnet._config.num_layers == 24
        assert bitnet._config.hidden_dim == 1536

    def test_load_model_config_2b(self):
        """Test config for the 2B model."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)
        assert bitnet._config.num_layers == 30
        assert bitnet._config.hidden_dim == 2048

    def test_load_model_config_8b(self):
        """Test config for the 8B model."""
        bitnet = BitNetNative()
        bitnet.load_model("Llama3-8B-1.58", auto_download=False)
        assert bitnet._config.num_layers == 32
        assert bitnet._config.hidden_dim == 4096

    def test_unload_model(self):
        """Unloading should clear model state."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-large", auto_download=False)
        assert bitnet.model_loaded is True

        bitnet.unload_model()
        assert bitnet.model_loaded is False
        assert bitnet._model_name is None
        assert bitnet._config is None


class TestBitNetNativeGenerate:
    """Tests for text generation."""

    def test_generate_simulation(self):
        """Generate should produce output in simulation mode."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)
        output = bitnet.generate("What is AI?", max_tokens=20)

        assert isinstance(output, str)
        assert len(output) > 0
        assert "ARIA simulation" in output

    def test_generate_without_model_raises(self):
        """Generate without loading a model should raise RuntimeError."""
        bitnet = BitNetNative()
        with pytest.raises(RuntimeError, match="No model loaded"):
            bitnet.generate("test")

    def test_generate_deterministic(self):
        """Same prompt should produce same output in simulation."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)

        output1 = bitnet.generate("Hello world", max_tokens=10)
        output2 = bitnet.generate("Hello world", max_tokens=10)
        assert output1 == output2

    def test_generate_different_prompts_different_output(self):
        """Different prompts should produce different output."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)

        output1 = bitnet.generate("What is AI?", max_tokens=10)
        output2 = bitnet.generate("How does gravity work?", max_tokens=10)
        assert output1 != output2

    def test_generate_includes_model_name(self):
        """Simulation output should include model name."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-large", auto_download=False)
        output = bitnet.generate("test", max_tokens=5)
        assert "BitNet-b1.58-large" in output


class TestBitNetNativeWithMock:
    """Tests using mocked native library."""

    def test_load_native_lib_success(self):
        """Test successful native library loading with mock."""
        mock_lib = MagicMock()
        mock_lib.bitnet_init.return_value = 0x12345678  # Fake context pointer
        mock_lib.bitnet_generate.return_value = 5
        mock_lib.bitnet_free.return_value = None

        with patch("ctypes.CDLL", return_value=mock_lib):
            bitnet = BitNetNative(lib_path="/fake/libbitnet.so")
            assert bitnet.is_native is True
            assert bitnet.is_simulation is False

    def test_native_generate_with_mock(self):
        """Test generation via mocked native library."""
        mock_lib = MagicMock()
        mock_lib.bitnet_init.return_value = 0x12345678
        mock_lib.bitnet_generate.return_value = 5
        mock_lib.bitnet_free.return_value = None

        with patch("ctypes.CDLL", return_value=mock_lib):
            bitnet = BitNetNative(lib_path="/fake/libbitnet.so")

            # Create a fake model directory with required files
            with tempfile.TemporaryDirectory() as tmpdir:
                model_dir = Path(tmpdir) / "BitNet-b1.58-2B-4T"
                model_dir.mkdir()
                (model_dir / "config.json").write_text("{}")
                (model_dir / "model.safetensors").write_bytes(b"\x00" * 100)

                # Use a custom model manager pointing to our temp dir
                manager = ModelManager(models_dir=Path(tmpdir))
                bitnet._model_manager = manager

                result = bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)
                assert result is True
                assert bitnet.model_loaded is True

    def test_native_lib_load_failure_falls_back(self):
        """If CDLL raises OSError, should fall back to simulation."""
        with patch("ctypes.CDLL", side_effect=OSError("lib not found")):
            bitnet = BitNetNative(lib_path="/fake/libbitnet.so")
            assert bitnet.is_simulation is True


class TestBitNetNativeStats:
    """Tests for get_stats method."""

    def test_stats_no_model(self):
        """Stats should work with no model loaded."""
        bitnet = BitNetNative()
        stats = bitnet.get_stats()

        assert stats["backend"] == "simulation"
        assert stats["model_loaded"] is False
        assert stats["model_name"] is None
        assert stats["simulation_mode"] is True

    def test_stats_with_model(self):
        """Stats should reflect loaded model."""
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T", auto_download=False)
        stats = bitnet.get_stats()

        assert stats["model_loaded"] is True
        assert stats["model_name"] == "BitNet-b1.58-2B-4T"
        assert stats["config"]["num_layers"] == 30
        assert stats["config"]["hidden_dim"] == 2048


# =============================================================================
# ModelManager Tests
# =============================================================================


class TestModelManager:
    """Tests for ModelManager."""

    def setup_method(self):
        """Create a temporary directory for test models."""
        self.tmpdir = tempfile.mkdtemp()
        self.manager = ModelManager(models_dir=Path(self.tmpdir))

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_list_models_empty(self):
        """list_models should return empty list when no models installed."""
        models = self.manager.list_models()
        assert models == []

    def test_get_model_path_not_installed(self):
        """get_model_path should return None for uninstalled model."""
        path = self.manager.get_model_path("BitNet-b1.58-large")
        assert path is None

    def test_get_model_path_installed(self):
        """get_model_path should return path for installed model."""
        model_dir = Path(self.tmpdir) / "BitNet-b1.58-large"
        model_dir.mkdir()
        (model_dir / "config.json").write_text("{}")

        path = self.manager.get_model_path("BitNet-b1.58-large")
        assert path is not None
        assert path == model_dir

    def test_list_models_with_installed(self):
        """list_models should return installed models."""
        model_dir = Path(self.tmpdir) / "BitNet-b1.58-2B-4T"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"test": true}')
        (model_dir / "model.safetensors").write_bytes(b"\x00" * 1024)

        models = self.manager.list_models()
        assert len(models) == 1
        assert models[0].name == "BitNet-b1.58-2B-4T"
        assert models[0].params == "2.4B"
        assert models[0].size_on_disk > 0

    def test_list_models_ignores_non_model_dirs(self):
        """list_models should ignore directories without config.json."""
        (Path(self.tmpdir) / "random_dir").mkdir()
        models = self.manager.list_models()
        assert models == []

    def test_download_model_unknown_raises(self):
        """download_model should raise ValueError for unknown model."""
        with pytest.raises(ValueError, match="Unknown model"):
            self.manager.download_model("nonexistent-model")

    def test_download_model_already_exists(self):
        """download_model should return path if model already exists."""
        model_dir = Path(self.tmpdir) / "BitNet-b1.58-large"
        model_dir.mkdir()
        (model_dir / "config.json").write_text("{}")

        path = self.manager.download_model("BitNet-b1.58-large")
        assert path == model_dir

    @patch("urllib.request.urlopen")
    def test_download_model_network_failure(self, mock_urlopen):
        """download_model should raise ConnectionError on network failure."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        with pytest.raises(ConnectionError, match="Failed to download"):
            self.manager.download_model("BitNet-b1.58-large", force=True)

    @patch("urllib.request.urlopen")
    def test_download_model_cleans_up_on_failure(self, mock_urlopen):
        """Partial downloads should be cleaned up on failure."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("fail")

        model_dir = Path(self.tmpdir) / "BitNet-b1.58-large"
        try:
            self.manager.download_model("BitNet-b1.58-large", force=True)
        except ConnectionError:
            pass

        assert not model_dir.exists()

    def test_get_model_config(self):
        """get_model_config should return correct config."""
        config = self.manager.get_model_config("BitNet-b1.58-2B-4T")
        assert config["params"] == "2.4B"
        assert config["num_layers"] == 30
        assert config["hidden_dim"] == 2048

    def test_get_model_config_unknown_raises(self):
        """get_model_config should raise ValueError for unknown model."""
        with pytest.raises(ValueError, match="Unknown model"):
            self.manager.get_model_config("nonexistent")

    def test_list_supported_models(self):
        """list_supported_models should return all supported models."""
        supported = ModelManager.list_supported_models()
        assert "BitNet-b1.58-large" in supported
        assert "BitNet-b1.58-2B-4T" in supported
        assert "Llama3-8B-1.58" in supported

    def test_delete_model(self):
        """delete_model should remove model directory."""
        model_dir = Path(self.tmpdir) / "BitNet-b1.58-large"
        model_dir.mkdir()
        (model_dir / "config.json").write_text("{}")

        assert self.manager.delete_model("BitNet-b1.58-large") is True
        assert not model_dir.exists()

    def test_delete_model_not_found(self):
        """delete_model should return False if model not found."""
        assert self.manager.delete_model("nonexistent") is False

    def test_format_size(self):
        """format_size should format bytes correctly."""
        assert "0.0 B" == ModelManager.format_size(0)
        assert "512.0 B" == ModelManager.format_size(512)
        assert "1.0 KB" == ModelManager.format_size(1024)
        assert "1.0 MB" == ModelManager.format_size(1024 * 1024)
        assert "1.0 GB" == ModelManager.format_size(1024 * 1024 * 1024)


# =============================================================================
# InferenceEngine Backend Tests
# =============================================================================


class TestInferenceEngineBackend:
    """Tests for InferenceEngine backend parameter."""

    def test_default_backend_simulation(self):
        """Default backend should be simulation."""
        engine = InferenceEngine(node_id="test")
        assert engine.backend == "simulation"
        assert engine._bitnet is None

    def test_auto_backend_falls_back(self):
        """Auto backend should fall back to simulation when lib unavailable."""
        engine = InferenceEngine(node_id="test", backend="auto")
        assert engine.backend == "auto"
        # BitNet should be initialized but in simulation mode
        assert engine._bitnet is not None
        assert engine._bitnet.is_simulation is True

    def test_invalid_backend_raises(self):
        """Invalid backend should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid backend"):
            InferenceEngine(node_id="test", backend="invalid")

    def test_simulation_backend_no_bitnet(self):
        """Simulation backend should not initialize BitNet."""
        engine = InferenceEngine(node_id="test", backend="simulation")
        assert engine._bitnet is None

    def test_stats_include_backend(self):
        """Engine stats should include backend info."""
        engine = InferenceEngine(node_id="test", backend="auto")
        engine.load_model("aria-2b-1bit", num_layers=4, hidden_dim=128)
        engine.infer(query="test", model_id="aria-2b-1bit", max_tokens=5)

        stats = engine.get_stats()
        assert "backend" in stats
        assert stats["backend"] == "auto"
        assert "native_available" in stats

    def test_auto_backend_still_works_for_inference(self):
        """Auto backend should still produce inference results."""
        engine = InferenceEngine(node_id="test", backend="auto")
        engine.load_model("aria-2b-1bit", num_layers=4, hidden_dim=128)

        result = engine.infer(query="test", model_id="aria-2b-1bit", max_tokens=5)
        assert result is not None
        assert result.tokens_generated >= 0
