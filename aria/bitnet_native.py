"""
ARIA Protocol - Native BitNet Integration
Provides Python bindings for bitnet.cpp via ctypes.

Falls back to simulation mode if the native library is not available.
Supports auto-download of models from HuggingFace.

MIT License - Anthony MURGO, 2026
"""

import ctypes
import ctypes.util
import hashlib
import logging
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from aria.model_manager import ModelManager, SUPPORTED_MODELS

logger = logging.getLogger(__name__)

# Library search paths
_LIB_SEARCH_PATHS = [
    Path.home() / ".aria" / "lib",
    Path("/usr/local/lib"),
    Path("/usr/lib"),
    Path.cwd() / "build",
    Path.cwd() / "build" / "Release",
]


@dataclass
class BitNetConfig:
    """Configuration for a BitNet model."""
    model_name: str
    model_path: Optional[Path]
    num_layers: int
    hidden_dim: int
    vocab_size: int = 32000
    max_seq_len: int = 2048
    num_heads: int = 16


class BitNetNative:
    """
    Native Python interface to bitnet.cpp.

    Uses ctypes to load the compiled bitnet.cpp shared library
    and provides a Pythonic interface for model loading and inference.

    Falls back to simulation mode if the native library is unavailable.

    Usage:
        bitnet = BitNetNative()
        bitnet.load_model("BitNet-b1.58-2B-4T")
        result = bitnet.generate("What is AI?", max_tokens=100)
    """

    def __init__(self, lib_path: Optional[str] = None,
                 model_manager: Optional[ModelManager] = None):
        """
        Initialize the BitNet native interface.

        Args:
            lib_path: Explicit path to bitnet.cpp shared library.
                      If None, auto-detects from standard locations.
            model_manager: ModelManager instance for model downloads.
                           If None, creates a default one.
        """
        self._lib = None
        self._lib_path: Optional[str] = lib_path
        self._model_loaded = False
        self._model_name: Optional[str] = None
        self._config: Optional[BitNetConfig] = None
        self._simulation_mode = False
        self._model_manager = model_manager or ModelManager()
        self._ctx = None  # Native context pointer

        # Try to load native library
        self._try_load_library()

    def _try_load_library(self):
        """Attempt to load the bitnet.cpp shared library."""
        if self._lib_path:
            if not self._load_from_path(self._lib_path):
                logger.warning(
                    "Failed to load specified library %s, using simulation mode",
                    self._lib_path,
                )
                self._simulation_mode = True
            return

        # Determine library name by platform
        system = platform.system()
        if system == "Linux":
            lib_name = "libbitnet.so"
        elif system == "Darwin":
            lib_name = "libbitnet.dylib"
        elif system == "Windows":
            lib_name = "bitnet.dll"
        else:
            logger.warning("Unsupported platform %s, using simulation mode", system)
            self._simulation_mode = True
            return

        # Search standard paths
        for search_dir in _LIB_SEARCH_PATHS:
            lib_file = search_dir / lib_name
            if lib_file.exists():
                if self._load_from_path(str(lib_file)):
                    return

        # Try system library path via ctypes.util
        system_lib = ctypes.util.find_library("bitnet")
        if system_lib:
            if self._load_from_path(system_lib):
                return

        # No library found - fall back to simulation
        logger.info(
            "bitnet.cpp library not found. Using simulation mode. "
            "To use native inference, compile bitnet.cpp and place "
            "libbitnet.so in ~/.aria/lib/ or /usr/local/lib/"
        )
        self._simulation_mode = True

    def _load_from_path(self, path: str) -> bool:
        """
        Load the shared library from a specific path.

        Args:
            path: Path to the shared library file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            self._lib = ctypes.CDLL(path)
            self._lib_path = path
            self._setup_bindings()
            self._simulation_mode = False
            logger.info("Loaded bitnet.cpp from %s", path)
            return True
        except OSError as e:
            logger.debug("Failed to load %s: %s", path, e)
            return False

    def _setup_bindings(self):
        """Configure ctypes function signatures for the native library."""
        if not self._lib:
            return

        # bitnet_init(model_path: str) -> ctx*
        self._lib.bitnet_init.argtypes = [ctypes.c_char_p]
        self._lib.bitnet_init.restype = ctypes.c_void_p

        # bitnet_generate(ctx*, prompt: str, max_tokens: int, output: char*, output_len: int) -> int
        self._lib.bitnet_generate.argtypes = [
            ctypes.c_void_p,    # ctx
            ctypes.c_char_p,    # prompt
            ctypes.c_int,       # max_tokens
            ctypes.c_char_p,    # output buffer
            ctypes.c_int,       # output buffer length
        ]
        self._lib.bitnet_generate.restype = ctypes.c_int

        # bitnet_free(ctx*) -> void
        self._lib.bitnet_free.argtypes = [ctypes.c_void_p]
        self._lib.bitnet_free.restype = None

    @property
    def is_native(self) -> bool:
        """Whether native bitnet.cpp is available."""
        return not self._simulation_mode

    @property
    def is_simulation(self) -> bool:
        """Whether running in simulation mode."""
        return self._simulation_mode

    @property
    def backend_name(self) -> str:
        """Name of the active backend."""
        return "native" if self.is_native else "simulation"

    @property
    def model_loaded(self) -> bool:
        """Whether a model is currently loaded."""
        return self._model_loaded

    def load_model(self, model_name: str, auto_download: bool = True) -> bool:
        """
        Load a BitNet model for inference.

        If the model is not locally available and auto_download is True,
        it will be downloaded from HuggingFace Hub automatically.

        Args:
            model_name: Name of the model (e.g., 'BitNet-b1.58-2B-4T')
            auto_download: Download model from HuggingFace if not present

        Returns:
            True if model loaded successfully

        Raises:
            ValueError: If model name is not supported
            ConnectionError: If download fails
            RuntimeError: If native loading fails
        """
        if model_name not in SUPPORTED_MODELS:
            available = ", ".join(SUPPORTED_MODELS.keys())
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Supported models: {available}"
            )

        meta = SUPPORTED_MODELS[model_name]

        # Check if model is locally available
        model_path = self._model_manager.get_model_path(model_name)

        if model_path is None and auto_download:
            print(f"Model {model_name} not found locally. Downloading...")
            model_path = self._model_manager.download_model(model_name)
            print(f"Model downloaded to {model_path}")

        # Create config
        self._config = BitNetConfig(
            model_name=model_name,
            model_path=model_path,
            num_layers=meta["num_layers"],
            hidden_dim=meta["hidden_dim"],
        )

        if self._simulation_mode:
            # Simulation mode: just mark as loaded
            self._model_loaded = True
            self._model_name = model_name
            logger.info("Model %s loaded in simulation mode", model_name)
            return True

        # Native mode: load via bitnet.cpp
        if model_path is None:
            raise RuntimeError(
                f"Model {model_name} not available locally and "
                f"auto_download is disabled"
            )

        model_file = model_path / "model.safetensors"
        if not model_file.exists():
            raise RuntimeError(f"Model file not found: {model_file}")

        ctx = self._lib.bitnet_init(str(model_file).encode("utf-8"))
        if not ctx:
            raise RuntimeError(f"Failed to initialize model {model_name}")

        # Free previous context if any
        if self._ctx:
            self._lib.bitnet_free(self._ctx)

        self._ctx = ctx
        self._model_loaded = True
        self._model_name = model_name
        logger.info("Model %s loaded natively from %s", model_name, model_path)
        return True

    def generate(self, prompt: str, max_tokens: int = 100,
                 temperature: float = 0.7) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 = greedy)

        Returns:
            Generated text string

        Raises:
            RuntimeError: If no model is loaded
        """
        if not self._model_loaded:
            raise RuntimeError("No model loaded. Call load_model() first.")

        if self._simulation_mode:
            return self._simulate_generate(prompt, max_tokens, temperature)

        # Native generation via bitnet.cpp
        output_buf_size = max_tokens * 16  # generous buffer
        output_buf = ctypes.create_string_buffer(output_buf_size)

        tokens_generated = self._lib.bitnet_generate(
            self._ctx,
            prompt.encode("utf-8"),
            max_tokens,
            output_buf,
            output_buf_size,
        )

        if tokens_generated < 0:
            raise RuntimeError("Native generation failed")

        return output_buf.value.decode("utf-8", errors="replace")

    def _simulate_generate(self, prompt: str, max_tokens: int,
                           temperature: float) -> str:
        """
        Simulate text generation when native library is unavailable.

        Produces deterministic output based on the input prompt hash,
        mimicking the behavior of a real model for protocol testing.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (unused in simulation)

        Returns:
            Simulated output text
        """
        # Deterministic simulation based on prompt hash
        prompt_hash = hashlib.sha256(prompt.encode()).digest()

        # Simulate processing time proportional to token count
        config = self._config
        if config:
            # Rough estimate: larger models are slower
            _base_delay = config.num_layers * 0.0001
        else:
            _base_delay = 0.001

        # Generate deterministic "tokens"
        words = [
            "the", "of", "and", "to", "in", "is", "that", "for",
            "it", "with", "as", "was", "on", "are", "be", "this",
            "have", "from", "or", "an", "by", "not", "but", "what",
            "all", "were", "when", "we", "there", "can", "which",
            "their", "if", "will", "each", "about", "how", "up",
            "out", "them", "then", "she", "many", "some", "so",
            "these", "would", "other", "into", "has", "more", "her",
            "two", "like", "him", "see", "time", "could", "no",
            "make", "than", "been", "its", "who", "did", "get",
        ]

        generated = []
        for i in range(min(max_tokens, 50)):
            idx = (prompt_hash[i % len(prompt_hash)] + i * 7) % len(words)
            generated.append(words[idx])

        return f"[ARIA simulation | model={self._model_name}] " + " ".join(generated)

    def get_stats(self) -> dict:
        """Get runtime statistics."""
        return {
            "backend": self.backend_name,
            "model_loaded": self._model_loaded,
            "model_name": self._model_name,
            "simulation_mode": self._simulation_mode,
            "lib_path": self._lib_path,
            "config": {
                "num_layers": self._config.num_layers if self._config else None,
                "hidden_dim": self._config.hidden_dim if self._config else None,
            } if self._config else None,
        }

    def unload_model(self):
        """Unload the current model and free resources."""
        if self._ctx and self._lib:
            self._lib.bitnet_free(self._ctx)
            self._ctx = None

        self._model_loaded = False
        self._model_name = None
        self._config = None

    def __del__(self):
        """Clean up native resources on deletion."""
        if self._ctx and self._lib:
            try:
                self._lib.bitnet_free(self._ctx)
            except Exception:
                pass

    def __repr__(self) -> str:
        mode = "native" if self.is_native else "simulation"
        model = self._model_name or "none"
        return f"BitNetNative(mode={mode}, model={model})"
