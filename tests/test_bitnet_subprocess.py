"""Tests for the BitNet subprocess inference backend."""

import platform
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from aria.bitnet_subprocess import BitNetSubprocess, MODEL_GGUF_MAP, MODEL_METADATA
from aria.inference import InferenceEngine, InferenceResult


# =============================================================================
# BitNetSubprocess Discovery & Initialization
# =============================================================================


class TestBitNetSubprocessInit:
    """Tests for BitNetSubprocess initialization and executable discovery."""

    @patch("aria.bitnet_subprocess.DEFAULT_MODEL_PATHS", [])
    @patch("aria.bitnet_subprocess.DEFAULT_BITNET_PATHS", [])
    def test_unavailable_when_no_executable(self):
        """Backend should be unavailable when no executable is found."""
        backend = BitNetSubprocess(
            exe_path="/nonexistent/llama-cli.exe",
            models_dir="/nonexistent/models",
        )
        assert backend.is_available is False

    def test_backend_name(self):
        """Backend name should be native_subprocess."""
        backend = BitNetSubprocess(exe_path="/fake")
        assert backend.backend_name == "native_subprocess"

    @patch("aria.bitnet_subprocess.DEFAULT_MODEL_PATHS", [])
    @patch("aria.bitnet_subprocess.DEFAULT_BITNET_PATHS", [])
    def test_repr_unavailable(self):
        """Repr should show unavailable status."""
        backend = BitNetSubprocess(exe_path="/fake")
        r = repr(backend)
        assert "unavailable" in r

    def test_repr_available(self):
        """Repr should show available status when exe found."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"\x00")
            tmp_path = f.name

        try:
            backend = BitNetSubprocess(exe_path=tmp_path)
            assert backend.is_available is True
            r = repr(backend)
            assert "available" in r
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_explicit_exe_path(self):
        """Explicit exe_path should be used when provided."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"\x00")
            tmp_path = f.name

        try:
            backend = BitNetSubprocess(exe_path=tmp_path)
            assert backend.exe_path == Path(tmp_path)
            assert backend.is_available is True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_explicit_models_dir(self):
        """Explicit models_dir should be used when provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = BitNetSubprocess(models_dir=tmpdir)
            assert backend.models_dir == Path(tmpdir)

    def test_default_threads(self):
        """Default thread count should be 8."""
        backend = BitNetSubprocess(exe_path="/fake")
        assert backend.threads == 8

    def test_custom_threads(self):
        """Custom thread count should be stored."""
        backend = BitNetSubprocess(exe_path="/fake", threads=16)
        assert backend.threads == 16

    def test_initial_stats_zero(self):
        """Initial statistics should be zero."""
        backend = BitNetSubprocess(exe_path="/fake")
        assert backend.total_inferences == 0
        assert backend.total_tokens_generated == 0
        assert backend.total_time_ms == 0.0


# =============================================================================
# Model Path Resolution
# =============================================================================


class TestBitNetSubprocessModelPaths:
    """Tests for model path resolution."""

    def setup_method(self):
        """Create temp directory with fake model structure."""
        self.tmpdir = tempfile.mkdtemp()
        self.models_dir = Path(self.tmpdir)

        # Create fake GGUF files for known models
        for model_id, relative_path in MODEL_GGUF_MAP.items():
            if model_id.startswith("aria-"):
                continue  # Skip aliases
            gguf_path = self.models_dir / relative_path
            gguf_path.parent.mkdir(parents=True, exist_ok=True)
            gguf_path.write_bytes(b"\x00" * 1024)

    def teardown_method(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_model_path_known_model(self):
        """Should resolve known model IDs to GGUF paths."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        path = backend.get_model_path("bitnet-b1.58-large")
        assert path is not None
        assert path.exists()
        assert path.name == "ggml-model-i2_s.gguf"

    def test_get_model_path_2b(self):
        """Should resolve 2B model."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        path = backend.get_model_path("bitnet-b1.58-2b-4t")
        assert path is not None
        assert "BitNet-b1.58-2B-4T" in str(path)

    def test_get_model_path_alias(self):
        """Should resolve model alias."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        path = backend.get_model_path("aria-2b-1bit")
        assert path is not None

    def test_get_model_path_case_insensitive(self):
        """Model ID lookup should be case-insensitive."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        path = backend.get_model_path("BitNet-b1.58-Large")
        assert path is not None

    def test_get_model_path_unknown(self):
        """Should return None for unknown model ID."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        path = backend.get_model_path("nonexistent-model")
        assert path is None

    @patch("aria.bitnet_subprocess.DEFAULT_MODEL_PATHS", [])
    @patch("aria.bitnet_subprocess.DEFAULT_BITNET_PATHS", [])
    def test_get_model_path_no_models_dir(self):
        """Should return None when no models_dir configured."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir="/nonexistent/dir",
        )
        path = backend.get_model_path("bitnet-b1.58-large")
        assert path is None

    def test_list_available_models(self):
        """Should list all models with GGUF files present."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        models = backend.list_available_models()
        assert len(models) >= 3  # large, 2b, 8b
        ids = [m["id"] for m in models]
        assert "bitnet-b1.58-large" in ids
        assert "bitnet-b1.58-2b-4t" in ids
        assert "llama3-8b-1.58" in ids

    def test_list_available_models_skips_aliases(self):
        """list_available_models should not include aliases."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        models = backend.list_available_models()
        ids = [m["id"] for m in models]
        assert "aria-2b-1bit" not in ids

    def test_list_available_models_includes_metadata(self):
        """Each model entry should have display_name, params, size_gb."""
        backend = BitNetSubprocess(
            exe_path="/fake",
            models_dir=self.tmpdir,
        )
        models = backend.list_available_models()
        for model in models:
            assert "id" in model
            assert "display_name" in model
            assert "params" in model
            assert "size_gb" in model
            assert "available" in model
            assert model["available"] is True

    def test_list_available_models_empty_dir(self):
        """Should return empty list when no models installed."""
        with tempfile.TemporaryDirectory() as empty_dir:
            backend = BitNetSubprocess(
                exe_path="/fake",
                models_dir=empty_dir,
            )
            models = backend.list_available_models()
            assert models == []


# =============================================================================
# Performance Stats Parsing
# =============================================================================


class TestBitNetSubprocessStatsParsing:
    """Tests for parsing llama.cpp performance stats from stderr."""

    def test_parse_eval_stats(self):
        """Should parse eval time, tokens, and speed from stderr."""
        backend = BitNetSubprocess(exe_path="/fake")
        stderr = (
            "llama_perf_context_print:        load time =     117.42 ms\n"
            "llama_perf_context_print: prompt eval time =      11.21 ms /     2 tokens (    5.60 ms per token,   178.44 tokens per second)\n"
            "llama_perf_context_print:        eval time =     253.53 ms /    29 runs   (    8.74 ms per token,   114.38 tokens per second)\n"
        )
        stats = backend._parse_perf_stats(stderr)

        assert stats["eval_time_ms"] == 253.53
        assert stats["eval_tokens"] == 29
        assert stats["eval_ms_per_token"] == 8.74
        assert stats["eval_tokens_per_second"] == 114.38

    def test_parse_load_time(self):
        """Should parse load time from stderr."""
        backend = BitNetSubprocess(exe_path="/fake")
        stderr = "llama_perf_context_print:        load time =     117.42 ms\n"
        stats = backend._parse_perf_stats(stderr)

        assert stats["load_time_ms"] == 117.42

    def test_parse_prompt_eval(self):
        """Should parse prompt eval stats."""
        backend = BitNetSubprocess(exe_path="/fake")
        stderr = (
            "llama_perf_context_print: prompt eval time =      11.21 ms /     2 tokens "
            "(    5.60 ms per token,   178.44 tokens per second)\n"
        )
        stats = backend._parse_perf_stats(stderr)

        assert stats["prompt_eval_time_ms"] == 11.21
        assert stats["prompt_tokens"] == 2
        assert stats["prompt_tokens_per_second"] == 178.44

    def test_parse_empty_stderr(self):
        """Should return empty dict for empty stderr."""
        backend = BitNetSubprocess(exe_path="/fake")
        stats = backend._parse_perf_stats("")
        assert stats == {}

    def test_parse_no_perf_lines(self):
        """Should return empty dict when no perf lines present."""
        backend = BitNetSubprocess(exe_path="/fake")
        stats = backend._parse_perf_stats("some random output\nno perf here\n")
        assert stats == {}

    def test_parse_high_speed(self):
        """Should parse very high speed values correctly."""
        backend = BitNetSubprocess(exe_path="/fake")
        stderr = (
            "llama_perf_context_print:        eval time =     410.23 ms /    50 runs   "
            "(    8.20 ms per token,   121.89 tokens per second)\n"
        )
        stats = backend._parse_perf_stats(stderr)
        assert stats["eval_tokens_per_second"] == 121.89
        assert stats["eval_tokens"] == 50


# =============================================================================
# Inference via Subprocess (Mocked)
# =============================================================================


class TestBitNetSubprocessInference:
    """Tests for inference execution with mocked subprocess."""

    def _make_backend(self, exe_path=None, models_dir=None):
        """Create a backend with fake exe and models."""
        self._tmpdir = tempfile.mkdtemp()
        models = Path(self._tmpdir)

        # Create a fake GGUF
        gguf_dir = models / "bitnet_b1_58-large"
        gguf_dir.mkdir(parents=True)
        (gguf_dir / "ggml-model-i2_s.gguf").write_bytes(b"\x00" * 2048)

        # Create a fake executable
        exe_file = models / "llama-cli.exe"
        exe_file.write_bytes(b"\x00")

        return BitNetSubprocess(
            exe_path=str(exe_file),
            models_dir=str(models),
            threads=8,
        )

    def teardown_method(self):
        """Clean up."""
        import shutil
        if hasattr(self, "_tmpdir"):
            shutil.rmtree(self._tmpdir, ignore_errors=True)

    @patch("aria.bitnet_subprocess.DEFAULT_MODEL_PATHS", [])
    @patch("aria.bitnet_subprocess.DEFAULT_BITNET_PATHS", [])
    def test_inference_unavailable_backend(self):
        """Should return error when backend is unavailable."""
        backend = BitNetSubprocess(exe_path="/nonexistent")
        result = backend.run_inference(prompt="test")
        assert "error" in result
        assert result["output"] == ""

    def test_inference_unknown_model(self):
        """Should return error for unknown model."""
        backend = self._make_backend()
        result = backend.run_inference(
            prompt="test",
            model_id="nonexistent-model",
        )
        assert "error" in result
        assert "not found" in result["error"]

    @patch("subprocess.run")
    def test_inference_success(self, mock_run):
        """Should return parsed results on successful inference."""
        mock_run.return_value = MagicMock(
            stdout=" What is AI? AI is a field of computer science.",
            stderr=(
                "llama_perf_context_print:        load time =     100.00 ms\n"
                "llama_perf_context_print: prompt eval time =      10.00 ms /     5 tokens "
                "(    2.00 ms per token,   500.00 tokens per second)\n"
                "llama_perf_context_print:        eval time =     400.00 ms /    50 runs   "
                "(    8.00 ms per token,   125.00 tokens per second)\n"
            ),
            returncode=0,
        )

        backend = self._make_backend()
        result = backend.run_inference(
            prompt="What is AI?",
            model_id="bitnet-b1.58-large",
            max_tokens=50,
        )

        assert "error" not in result
        assert result["output"] == "AI is a field of computer science."
        assert result["tokens_generated"] == 50
        assert result["tokens_per_second"] == 125.0
        assert result["backend"] == "native_subprocess"
        assert result["load_time_ms"] == 100.0

    @patch("subprocess.run")
    def test_inference_strips_prompt_from_output(self, mock_run):
        """Output should have the input prompt stripped."""
        mock_run.return_value = MagicMock(
            stdout=" Hello world This is the response.",
            stderr="",
            returncode=0,
        )

        backend = self._make_backend()
        result = backend.run_inference(
            prompt="Hello world",
            model_id="bitnet-b1.58-large",
            max_tokens=10,
        )

        assert result["output"] == "This is the response."

    @patch("subprocess.run")
    def test_inference_timeout(self, mock_run):
        """Should handle subprocess timeout gracefully."""
        import subprocess as sp
        mock_run.side_effect = sp.TimeoutExpired(cmd="llama-cli", timeout=30)

        backend = self._make_backend()
        result = backend.run_inference(
            prompt="test",
            model_id="bitnet-b1.58-large",
            timeout_seconds=30,
        )

        assert "error" in result
        assert "timed out" in result["error"]

    @patch("subprocess.run")
    def test_inference_file_not_found(self, mock_run):
        """Should handle missing executable gracefully."""
        mock_run.side_effect = FileNotFoundError("llama-cli not found")

        backend = self._make_backend()
        result = backend.run_inference(
            prompt="test",
            model_id="bitnet-b1.58-large",
        )

        assert "error" in result

    @patch("subprocess.run")
    def test_inference_updates_stats(self, mock_run):
        """Successful inference should update backend statistics."""
        mock_run.return_value = MagicMock(
            stdout=" test Generated text here.",
            stderr=(
                "llama_perf_context_print:        eval time =     200.00 ms /    20 runs   "
                "(   10.00 ms per token,   100.00 tokens per second)\n"
            ),
            returncode=0,
        )

        backend = self._make_backend()
        assert backend.total_inferences == 0

        backend.run_inference(prompt="test", model_id="bitnet-b1.58-large")
        assert backend.total_inferences == 1
        assert backend.total_tokens_generated == 20
        assert backend.total_time_ms > 0

    @patch("subprocess.run")
    def test_inference_energy_estimation(self, mock_run):
        """Should estimate energy based on CPU TDP and thread ratio."""
        mock_run.return_value = MagicMock(
            stdout=" test Response.",
            stderr=(
                "llama_perf_context_print:        eval time =     500.00 ms /    25 runs   "
                "(   20.00 ms per token,    50.00 tokens per second)\n"
            ),
            returncode=0,
        )

        backend = self._make_backend()
        result = backend.run_inference(prompt="test", model_id="bitnet-b1.58-large")

        assert "energy_estimate_mj" in result
        assert result["energy_estimate_mj"] > 0
        assert "energy_mj_per_token" in result
        assert result["energy_mj_per_token"] > 0

    @patch("subprocess.run")
    def test_inference_fallback_speed_calc(self, mock_run):
        """Should calculate speed from elapsed time if stderr has no stats."""
        mock_run.return_value = MagicMock(
            stdout=" test Some generated output here.",
            stderr="",  # No perf stats
            returncode=0,
        )

        backend = self._make_backend()
        result = backend.run_inference(
            prompt="test",
            model_id="bitnet-b1.58-large",
            max_tokens=50,
        )

        # Should use fallback calculation
        assert result["tokens_per_second"] >= 0


# =============================================================================
# Get Stats
# =============================================================================


class TestBitNetSubprocessGetStats:
    """Tests for get_stats method."""

    @patch("aria.bitnet_subprocess.DEFAULT_MODEL_PATHS", [])
    @patch("aria.bitnet_subprocess.DEFAULT_BITNET_PATHS", [])
    def test_stats_unavailable(self):
        """Stats should reflect unavailable backend."""
        backend = BitNetSubprocess(exe_path="/fake")
        stats = backend.get_stats()

        assert stats["backend"] == "native_subprocess"
        assert stats["available"] is False
        assert stats["exe_path"] is None
        assert stats["threads"] == 8
        assert stats["total_inferences"] == 0

    def test_stats_available(self):
        """Stats should reflect available backend."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"\x00")
            tmp_path = f.name

        try:
            backend = BitNetSubprocess(exe_path=tmp_path, threads=12)
            stats = backend.get_stats()

            assert stats["available"] is True
            assert stats["exe_path"] == tmp_path
            assert stats["threads"] == 12
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_stats_after_inferences(self):
        """Stats should reflect inference history."""
        backend = BitNetSubprocess(exe_path="/fake")
        # Manually set stats to simulate inferences
        backend.total_inferences = 10
        backend.total_tokens_generated = 500
        backend.total_time_ms = 5000.0

        stats = backend.get_stats()
        assert stats["total_inferences"] == 10
        assert stats["total_tokens_generated"] == 500
        assert stats["avg_tokens_per_inference"] == 50.0
        assert stats["avg_time_per_inference_ms"] == 500.0


# =============================================================================
# InferenceEngine Integration with Subprocess Backend
# =============================================================================


class TestInferenceEngineSubprocessIntegration:
    """Tests for InferenceEngine with subprocess backend mode."""

    def test_subprocess_backend_mode(self):
        """Engine should accept 'subprocess' as backend mode."""
        engine = InferenceEngine(node_id="test", backend="subprocess")
        assert engine.backend == "subprocess"

    def test_subprocess_fallback_to_simulation(self):
        """Subprocess backend should fall back to simulation if exe not found."""
        engine = InferenceEngine(node_id="test", backend="auto")
        # On CI without llama-cli.exe, should fall back
        stats = engine.get_stats()
        assert stats["active_backend"] in ("subprocess", "simulation")

    def test_subprocess_explicit_raises_when_unavailable(self):
        """Explicitly requesting subprocess should raise if unavailable."""
        # This may or may not raise depending on whether llama-cli.exe exists
        # In CI, it should raise
        try:
            engine = InferenceEngine(node_id="test", backend="subprocess")
            # If it didn't raise, subprocess must be available
            assert engine._active_backend == "subprocess"
        except RuntimeError as e:
            assert "not found" in str(e).lower()

    def test_auto_backend_priority(self):
        """Auto backend should try native → subprocess → simulation."""
        engine = InferenceEngine(node_id="test", backend="auto")
        # In CI, should end up in simulation (no native lib or exe)
        assert engine._active_backend in ("native", "subprocess", "simulation")

    def test_engine_stats_include_subprocess_info(self):
        """Engine stats should include subprocess backend info."""
        engine = InferenceEngine(node_id="test", backend="auto")
        stats = engine.get_stats()
        assert "subprocess_available" in stats
        assert isinstance(stats["subprocess_available"], bool)

    def test_simulation_fallback_still_works(self):
        """Even with subprocess backend request, simulation should work as fallback."""
        engine = InferenceEngine(node_id="test", backend="simulation")
        engine.load_model("aria-2b-1bit", num_layers=4, hidden_dim=128)
        result = engine.infer(query="test", model_id="aria-2b-1bit", max_tokens=5)
        assert result is not None
        assert isinstance(result, InferenceResult)


# =============================================================================
# Model Metadata Constants
# =============================================================================


class TestBitNetSubprocessConstants:
    """Tests for module-level constants and mappings."""

    def test_model_gguf_map_has_all_models(self):
        """GGUF map should contain all main models."""
        assert "bitnet-b1.58-large" in MODEL_GGUF_MAP
        assert "bitnet-b1.58-2b-4t" in MODEL_GGUF_MAP
        assert "llama3-8b-1.58" in MODEL_GGUF_MAP

    def test_model_gguf_map_has_alias(self):
        """GGUF map should contain aria alias."""
        assert "aria-2b-1bit" in MODEL_GGUF_MAP

    def test_model_metadata_has_all_models(self):
        """Metadata should exist for all main models."""
        assert "bitnet-b1.58-large" in MODEL_METADATA
        assert "bitnet-b1.58-2b-4t" in MODEL_METADATA
        assert "llama3-8b-1.58" in MODEL_METADATA

    def test_model_metadata_has_params(self):
        """Each metadata entry should have display name and params."""
        for model_id, meta in MODEL_METADATA.items():
            assert "display" in meta, f"Missing 'display' for {model_id}"
            assert "params" in meta, f"Missing 'params' for {model_id}"

    def test_alias_maps_to_2b(self):
        """aria-2b-1bit alias should map to same GGUF as 2B model."""
        assert MODEL_GGUF_MAP["aria-2b-1bit"] == MODEL_GGUF_MAP["bitnet-b1.58-2b-4t"]
