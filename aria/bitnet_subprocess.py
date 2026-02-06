"""
ARIA Protocol - BitNet Subprocess Inference Backend.

Uses compiled llama-cli.exe (from bitnet.cpp) for real 1-bit inference
via subprocess. This is the pragmatic approach when bitnet.dll is not
available but the CLI tools are compiled.

Advantages:
- Uses actual bitnet.cpp inference (not simulation)
- Works with existing llama-cli.exe builds
- No need to modify bitnet.cpp to export DLL functions

MIT License - Anthony MURGO, 2026
"""

import asyncio
import logging
import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Default paths to search for bitnet executables
DEFAULT_BITNET_PATHS = [
    Path.home() / "Documents" / "BitNet" / "build" / "bin" / "Release",
    Path.home() / ".aria" / "bin",
    Path.home() / "BitNet" / "build" / "bin" / "Release",
    Path.cwd() / "bitnet" / "build" / "bin" / "Release",
]

# Default paths to search for models
DEFAULT_MODEL_PATHS = [
    Path.home() / "Documents" / "BitNet" / "models",
    Path.home() / ".aria" / "models",
    Path.cwd() / "models",
]

# Model name to GGUF relative path mapping
MODEL_GGUF_MAP = {
    "bitnet-b1.58-large": "bitnet_b1_58-large/ggml-model-i2_s.gguf",
    "bitnet-b1.58-2b-4t": "BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
    "llama3-8b-1.58": "Llama3-8B-1.58-100B-tokens/ggml-model-i2_s.gguf",
    # Aliases for backward compatibility
    "aria-2b-1bit": "BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf",
}

# Model metadata for display
MODEL_METADATA = {
    "bitnet-b1.58-large": {"display": "BitNet b1.58 Large", "params": "0.7B"},
    "bitnet-b1.58-2b-4t": {"display": "BitNet b1.58 2B 4T", "params": "2.4B"},
    "llama3-8b-1.58": {"display": "Llama3 8B 1.58", "params": "8.0B"},
    "aria-2b-1bit": {"display": "ARIA 2B 1-bit (alias)", "params": "2.4B"},
}


class BitNetSubprocess:
    """
    Inference backend using compiled llama-cli.exe as subprocess.

    Provides real 1-bit LLM inference on CPU using the bitnet.cpp
    implementation via subprocess calls.

    Usage:
        backend = BitNetSubprocess(threads=8)
        if backend.is_available:
            result = backend.run_inference(
                prompt="What is AI?",
                model_id="bitnet-b1.58-large",
                max_tokens=100
            )
            print(result["output"])
            print(f"Speed: {result['tokens_per_second']} tok/s")
    """

    def __init__(
        self,
        exe_path: Optional[str] = None,
        models_dir: Optional[str] = None,
        threads: int = 8
    ):
        """
        Initialize the BitNet subprocess backend.

        Args:
            exe_path: Explicit path to llama-cli executable.
                      If None, auto-detects from standard locations.
            models_dir: Explicit path to models directory.
                        If None, auto-detects from standard locations.
            threads: Number of CPU threads to use for inference.
        """
        self.exe_path = self._find_executable(exe_path)
        self.models_dir = self._find_models_dir(models_dir)
        self.threads = threads
        self._available = self.exe_path is not None

        # Statistics
        self.total_inferences = 0
        self.total_tokens_generated = 0
        self.total_time_ms = 0.0

        if self._available:
            logger.info(f"BitNet subprocess backend initialized: {self.exe_path}")
            logger.info(f"Models directory: {self.models_dir}")
        else:
            logger.warning(
                "BitNet executable not found. Subprocess backend unavailable. "
                "Expected llama-cli.exe in one of: " +
                ", ".join(str(p) for p in DEFAULT_BITNET_PATHS)
            )

    def _find_executable(self, explicit_path: Optional[str] = None) -> Optional[Path]:
        """Find llama-cli executable.

        Search order:
        1. Explicit path passed as argument
        2. ARIA_LLAMA_CLI_PATH environment variable
        3. Standard search directories (DEFAULT_BITNET_PATHS)
        4. System PATH via shutil.which
        """
        exe_name = "llama-cli.exe" if platform.system() == "Windows" else "llama-cli"

        # 1. Explicit argument
        if explicit_path:
            p = Path(explicit_path)
            if p.exists():
                return p

        # 2. Environment variable
        env_path = os.environ.get("ARIA_LLAMA_CLI_PATH")
        if env_path:
            p = Path(env_path)
            if p.exists():
                return p

        # 3. Standard directories
        for search_dir in DEFAULT_BITNET_PATHS:
            candidate = search_dir / exe_name
            if candidate.exists():
                return candidate

        # 4. System PATH
        which_result = shutil.which(exe_name)
        if which_result:
            return Path(which_result)

        return None

    def _find_models_dir(self, explicit_dir: Optional[str] = None) -> Optional[Path]:
        """Find models directory."""
        if explicit_dir:
            p = Path(explicit_dir)
            if p.exists():
                return p

        for search_dir in DEFAULT_MODEL_PATHS:
            if search_dir.exists():
                return search_dir

        return None

    @property
    def is_available(self) -> bool:
        """Whether the subprocess backend is available."""
        return self._available

    @property
    def backend_name(self) -> str:
        """Name of this backend."""
        return "native_subprocess"

    def get_model_path(self, model_id: str) -> Optional[Path]:
        """
        Resolve model ID to GGUF file path.

        Args:
            model_id: Model identifier (e.g., "bitnet-b1.58-large")

        Returns:
            Full path to the GGUF file, or None if not found.
        """
        if not self.models_dir:
            return None

        # Try direct mapping first
        relative = MODEL_GGUF_MAP.get(model_id.lower())
        if relative:
            full_path = self.models_dir / relative
            if full_path.exists():
                return full_path

        # Try fuzzy match on directory name
        for subdir in self.models_dir.iterdir():
            if subdir.is_dir():
                gguf = subdir / "ggml-model-i2_s.gguf"
                if gguf.exists() and model_id.lower() in subdir.name.lower():
                    return gguf

        return None

    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List models that have GGUF files available locally.

        Returns:
            List of dicts with model info including id, path, size.
        """
        models = []
        if not self.models_dir:
            return models

        for model_id, relative_path in MODEL_GGUF_MAP.items():
            if model_id.startswith("aria-"):  # skip aliases
                continue

            full_path = self.models_dir / relative_path
            if full_path.exists():
                size_gb = round(full_path.stat().st_size / (1024**3), 2)
                meta = MODEL_METADATA.get(model_id, {})
                models.append({
                    "id": model_id,
                    "display_name": meta.get("display", model_id),
                    "params": meta.get("params", "unknown"),
                    "path": str(full_path),
                    "size_gb": size_gb,
                    "available": True,
                })

        return models

    def run_inference(
        self,
        prompt: str,
        model_id: str = "bitnet-b1.58-2b-4t",
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.95,
        timeout_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        Run inference using llama-cli.exe subprocess.

        Args:
            prompt: Input text prompt
            model_id: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = greedy)
            top_p: Top-p (nucleus) sampling parameter
            timeout_seconds: Maximum time to wait for inference

        Returns:
            Dict containing:
                - output: Generated text
                - tokens_generated: Number of tokens produced
                - tokens_per_second: Generation speed
                - time_ms: Total inference time in milliseconds
                - model: Model ID used
                - energy_estimate_mj: Estimated energy consumption
                - energy_mj_per_token: Energy per token
                - backend: Backend name ("native_subprocess")
                - error: Error message if failed (optional)
        """
        if not self._available:
            return {
                "error": "BitNet executable not found",
                "output": "",
                "backend": self.backend_name,
            }

        model_path = self.get_model_path(model_id)
        if not model_path:
            return {
                "error": f"Model {model_id} not found locally",
                "output": "",
                "backend": self.backend_name,
            }

        # Build command
        # Note: --log-disable suppresses stderr logging
        # The output includes the prompt, so we strip it manually
        cmd = [
            str(self.exe_path),
            "-m", str(model_path),
            "-p", prompt,
            "-n", str(max_tokens),
            "--threads", str(self.threads),
            "--temp", str(temperature),
            "--top-p", str(top_p),
            "--repeat-penalty", "1.1",
        ]

        logger.info(
            f"Running inference: model={model_id}, max_tokens={max_tokens}, "
            f"threads={self.threads}"
        )

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout_seconds,
                cwd=str(self.exe_path.parent),  # DLLs are in the same dir
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Parse output - strip the prompt prefix if present
            output_text = result.stdout.strip()
            # The output format is: " <prompt><generated_text>\n\n"
            # We need to remove the leading space and prompt
            if output_text.startswith(" " + prompt):
                output_text = output_text[len(" " + prompt):].strip()
            elif output_text.startswith(prompt):
                output_text = output_text[len(prompt):].strip()

            # Parse performance stats from stderr
            stderr = result.stderr or ""
            stats = self._parse_perf_stats(stderr)

            tokens_generated = stats.get("eval_tokens", max_tokens)
            tokens_per_second = stats.get("eval_tokens_per_second", 0)

            # Fallback calculation if stats not parsed
            if tokens_per_second == 0 and tokens_generated > 0 and elapsed_ms > 0:
                tokens_per_second = round(tokens_generated / (elapsed_ms / 1000), 2)

            # Estimate energy based on CPU TDP and thread utilization
            # Ryzen 9 7845HX TDP ~45W, 24 threads total
            cpu_tdp_w = 45
            total_threads = 24
            thread_ratio = self.threads / total_threads
            power_w = cpu_tdp_w * thread_ratio
            energy_j = power_w * (elapsed_ms / 1000)
            energy_mj = energy_j * 1000
            energy_mj_per_token = round(
                energy_mj / max(tokens_generated, 1), 2
            )

            # Update statistics
            self.total_inferences += 1
            self.total_tokens_generated += tokens_generated
            self.total_time_ms += elapsed_ms

            return {
                "output": output_text,
                "tokens_generated": tokens_generated,
                "tokens_per_second": round(tokens_per_second, 2),
                "time_ms": round(elapsed_ms, 2),
                "model": model_id,
                "energy_estimate_mj": round(energy_mj, 2),
                "energy_mj_per_token": energy_mj_per_token,
                "backend": self.backend_name,
                "load_time_ms": stats.get("load_time_ms", 0),
                "prompt_tokens": stats.get("prompt_tokens", 0),
            }

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.time() - start_time) * 1000
            return {
                "error": f"Inference timed out (>{timeout_seconds}s)",
                "output": "",
                "time_ms": round(elapsed_ms, 2),
                "backend": self.backend_name,
            }
        except FileNotFoundError:
            return {
                "error": f"Executable not found: {self.exe_path}",
                "output": "",
                "backend": self.backend_name,
            }
        except Exception as e:
            logger.error(f"Subprocess inference failed: {e}")
            return {
                "error": str(e),
                "output": "",
                "backend": self.backend_name,
            }

    def _parse_perf_stats(self, stderr: str) -> Dict[str, float]:
        """
        Parse llama.cpp performance stats from stderr.

        Example stderr output (llama_perf_context_print format):
            llama_perf_context_print:        load time =     117.42 ms
            llama_perf_context_print: prompt eval time =      11.21 ms /     2 tokens
            llama_perf_context_print:        eval time =     253.53 ms /    29 runs   (    8.74 ms per token,   114.38 tokens per second)

        Returns:
            Dict with parsed stats (eval_tokens, eval_tokens_per_second, etc.)
        """
        stats = {}

        # Pattern for generation eval time (not prompt eval)
        # llama_perf_context_print:        eval time =     253.53 ms /    29 runs   (    8.74 ms per token,   114.38 tokens per second)
        eval_match = re.search(
            r"llama_perf_context_print:\s+eval time\s*=\s*([\d.]+)\s*ms\s*/\s*(\d+)\s*(?:runs?|tokens?)"
            r"\s*\(\s*([\d.]+)\s*ms per token,\s*([\d.]+)\s*tokens per second\)",
            stderr
        )
        if eval_match:
            stats["eval_time_ms"] = float(eval_match.group(1))
            stats["eval_tokens"] = int(eval_match.group(2))
            stats["eval_ms_per_token"] = float(eval_match.group(3))
            stats["eval_tokens_per_second"] = float(eval_match.group(4))

        # Pattern for prompt eval time
        # llama_perf_context_print: prompt eval time =      11.21 ms /     2 tokens (    5.60 ms per token,   178.44 tokens per second)
        prompt_match = re.search(
            r"llama_perf_context_print:\s*prompt eval time\s*=\s*([\d.]+)\s*ms\s*/\s*(\d+)\s*tokens?"
            r"\s*\(\s*([\d.]+)\s*ms per token,\s*([\d.]+)\s*tokens per second\)",
            stderr
        )
        if prompt_match:
            stats["prompt_eval_time_ms"] = float(prompt_match.group(1))
            stats["prompt_tokens"] = int(prompt_match.group(2))
            stats["prompt_tokens_per_second"] = float(prompt_match.group(4))

        # Pattern for load time
        # llama_perf_context_print:        load time =     117.42 ms
        load_match = re.search(
            r"llama_perf_context_print:\s+load time\s*=\s*([\d.]+)\s*ms",
            stderr
        )
        if load_match:
            stats["load_time_ms"] = float(load_match.group(1))

        return stats

    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        avg_tokens_per_inference = (
            self.total_tokens_generated / self.total_inferences
            if self.total_inferences > 0 else 0
        )
        avg_time_per_inference = (
            self.total_time_ms / self.total_inferences
            if self.total_inferences > 0 else 0
        )

        return {
            "backend": self.backend_name,
            "available": self._available,
            "exe_path": str(self.exe_path) if self.exe_path else None,
            "models_dir": str(self.models_dir) if self.models_dir else None,
            "threads": self.threads,
            "total_inferences": self.total_inferences,
            "total_tokens_generated": self.total_tokens_generated,
            "total_time_ms": round(self.total_time_ms, 2),
            "avg_tokens_per_inference": round(avg_tokens_per_inference, 1),
            "avg_time_per_inference_ms": round(avg_time_per_inference, 2),
            "available_models": [m["id"] for m in self.list_available_models()],
        }

    def __repr__(self) -> str:
        status = "available" if self._available else "unavailable"
        return (
            f"BitNetSubprocess(status={status}, exe={self.exe_path}, "
            f"threads={self.threads})"
        )


# =========================================================================
# Module-level async convenience functions
# =========================================================================

# Lazy-initialized default backend instance
_default_backend: Optional[BitNetSubprocess] = None


def _get_default_backend() -> BitNetSubprocess:
    """Get or create the default backend singleton."""
    global _default_backend
    if _default_backend is None:
        _default_backend = BitNetSubprocess()
    return _default_backend


async def run_inference(
    model_path: str,
    prompt: str,
    max_tokens: int = 256,
    threads: int = 8,
    temperature: float = 0.7,
    llama_cli_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run inference via llama-cli subprocess (async wrapper).

    This is a module-level convenience function that wraps
    BitNetSubprocess.run_inference in asyncio.to_thread.

    Args:
        model_path: Path to the GGUF model file, or a model ID
                    that can be resolved by the backend.
        prompt: Input text prompt.
        max_tokens: Maximum tokens to generate.
        threads: Number of CPU threads to use.
        temperature: Sampling temperature.
        llama_cli_path: Explicit path to llama-cli executable.

    Returns:
        Dict with keys: text, tokens_generated, tokens_per_second,
        energy_mj, model, backend.
    """
    backend = BitNetSubprocess(
        exe_path=llama_cli_path,
        threads=threads,
    ) if llama_cli_path else _get_default_backend()

    # Determine if model_path is a file path or a model ID
    model_id = model_path
    if Path(model_path).suffix == ".gguf" and Path(model_path).exists():
        # Direct GGUF path: need to override model resolution
        # Use the sync method in a thread
        def _run():
            if not backend.is_available:
                return {
                    "text": "",
                    "tokens_generated": 0,
                    "tokens_per_second": 0.0,
                    "energy_mj": 0.0,
                    "model": model_path,
                    "backend": "unavailable",
                    "error": "llama-cli not found",
                }
            cmd = [
                str(backend.exe_path),
                "-m", model_path,
                "-p", prompt,
                "-n", str(max_tokens),
                "--threads", str(threads),
                "--temp", str(temperature),
                "--repeat-penalty", "1.1",
            ]
            start_time = time.time()
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, encoding='utf-8',
                    timeout=120, cwd=str(backend.exe_path.parent),
                )
                elapsed_ms = (time.time() - start_time) * 1000
                output_text = result.stdout.strip()
                if output_text.startswith(" " + prompt):
                    output_text = output_text[len(" " + prompt):].strip()
                elif output_text.startswith(prompt):
                    output_text = output_text[len(prompt):].strip()
                stats = backend._parse_perf_stats(result.stderr or "")
                tps = stats.get("eval_tokens_per_second", 0)
                tg = stats.get("eval_tokens", max_tokens)
                energy_mj = 45 * (threads / 24) * (elapsed_ms / 1000) * 1000
                return {
                    "text": output_text,
                    "tokens_generated": tg,
                    "tokens_per_second": round(tps, 2),
                    "energy_mj": round(energy_mj, 2),
                    "model": model_path,
                    "backend": "native",
                }
            except Exception as e:
                return {
                    "text": "",
                    "tokens_generated": 0,
                    "tokens_per_second": 0.0,
                    "energy_mj": 0.0,
                    "model": model_path,
                    "backend": "native",
                    "error": str(e),
                }
        return await asyncio.to_thread(_run)

    # Model ID path: use standard backend resolution
    def _run_by_id():
        result = backend.run_inference(
            prompt=prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return {
            "text": result.get("output", ""),
            "tokens_generated": result.get("tokens_generated", 0),
            "tokens_per_second": result.get("tokens_per_second", 0.0),
            "energy_mj": result.get("energy_estimate_mj", 0.0),
            "model": result.get("model", model_id),
            "backend": "native" if not result.get("error") else "unavailable",
            **({"error": result["error"]} if result.get("error") else {}),
        }

    return await asyncio.to_thread(_run_by_id)


async def check_backend_status() -> Dict[str, Any]:
    """
    Check the status of the native subprocess backend.

    Returns:
        Dict with keys: available, llama_cli_path, models, backend.
    """
    backend = _get_default_backend()
    models = backend.list_available_models()

    return {
        "available": backend.is_available,
        "llama_cli_path": str(backend.exe_path) if backend.exe_path else None,
        "models": models,
        "backend": "native" if backend.is_available else "unavailable",
    }


def list_available_models() -> List[Dict[str, Any]]:
    """
    List GGUF models available locally (sync convenience function).

    Scans ~/.aria/models/ and other standard locations for .gguf files.

    Returns:
        List of dicts with model info.
    """
    backend = _get_default_backend()
    return backend.list_available_models()


def scan_gguf_models(models_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan a directory for any .gguf model files.

    Unlike list_available_models which only finds known model IDs,
    this scans for ALL .gguf files in the directory tree.

    Args:
        models_dir: Directory to scan. Defaults to ~/.aria/models/.

    Returns:
        List of dicts with name, path, size_gb for each .gguf file found.
    """
    search_dir = Path(models_dir) if models_dir else Path.home() / ".aria" / "models"
    if not search_dir.exists():
        return []

    results = []
    for gguf_file in search_dir.rglob("*.gguf"):
        size_gb = round(gguf_file.stat().st_size / (1024**3), 2)
        # Derive a display name from the parent directory
        model_name = gguf_file.parent.name
        results.append({
            "name": model_name,
            "path": str(gguf_file),
            "size_gb": size_gb,
        })

    return results
