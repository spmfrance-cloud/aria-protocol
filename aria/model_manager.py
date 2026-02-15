"""
ARIA Protocol - Model Manager
Handles downloading, caching, and managing BitNet models.

Supports auto-download from HuggingFace with local caching
in ~/.aria/models/.

MIT License - Anthony MURGO, 2026
"""

import json
import shutil
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from aria import __version__


# Default cache directory
MODELS_DIR = Path.home() / ".aria" / "models"

# Supported models registry
SUPPORTED_MODELS: Dict[str, dict] = {
    "BitNet-b1.58-large": {
        "repo": "1bitLLM/bitnet_b1_58-large",
        "params": "0.7B",
        "description": "BitNet b1.58 Large (0.7B parameters)",
        "files": ["model.safetensors", "config.json", "tokenizer.json"],
        "num_layers": 24,
        "hidden_dim": 1536,
    },
    "BitNet-b1.58-2B-4T": {
        "repo": "1bitLLM/bitnet_b1_58-2B-4T",
        "params": "2.4B",
        "description": "BitNet b1.58 2B-4T (2.4B parameters)",
        "files": ["model.safetensors", "config.json", "tokenizer.json"],
        "num_layers": 30,
        "hidden_dim": 2048,
    },
    "Llama3-8B-1.58": {
        "repo": "HF1BitLLM/Llama3-8B-1.58-100B-tokens",
        "params": "8.0B",
        "description": "Llama3 8B 1.58-bit (8.0B parameters)",
        "files": ["model.safetensors", "config.json", "tokenizer.json"],
        "num_layers": 32,
        "hidden_dim": 4096,
    },
}


@dataclass
class ModelInfo:
    """Information about a locally installed model."""
    name: str
    path: Path
    params: str
    description: str
    num_layers: int
    hidden_dim: int
    size_on_disk: int  # bytes


class ModelManager:
    """
    Manages BitNet model downloads and local caching.

    Models are stored in ~/.aria/models/<model_name>/.
    Supports auto-download from HuggingFace Hub.
    """

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get the local path for a model.

        Args:
            model_name: Name of the model (e.g., 'BitNet-b1.58-large')

        Returns:
            Path to the model directory, or None if not installed
        """
        model_dir = self.models_dir / model_name
        if model_dir.exists() and (model_dir / "config.json").exists():
            return model_dir
        return None

    def list_models(self) -> List[ModelInfo]:
        """
        List all locally installed models.

        Returns:
            List of ModelInfo for each installed model
        """
        installed = []

        if not self.models_dir.exists():
            return installed

        for entry in sorted(self.models_dir.iterdir()):
            if not entry.is_dir():
                continue

            config_file = entry / "config.json"
            if not config_file.exists():
                continue

            # Get model metadata
            meta = SUPPORTED_MODELS.get(entry.name, {})

            # Calculate size on disk
            size = sum(
                f.stat().st_size
                for f in entry.rglob("*")
                if f.is_file()
            )

            installed.append(ModelInfo(
                name=entry.name,
                path=entry,
                params=meta.get("params", "unknown"),
                description=meta.get("description", entry.name),
                num_layers=meta.get("num_layers", 24),
                hidden_dim=meta.get("hidden_dim", 2048),
                size_on_disk=size,
            ))

        return installed

    def download_model(self, model_name: str, force: bool = False) -> Path:
        """
        Download a model from HuggingFace Hub.

        Args:
            model_name: Name of the model to download
            force: Re-download even if already present

        Returns:
            Path to the downloaded model directory

        Raises:
            ValueError: If model name is not in the supported list
            ConnectionError: If download fails
        """
        if model_name not in SUPPORTED_MODELS:
            available = ", ".join(SUPPORTED_MODELS.keys())
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Supported models: {available}"
            )

        model_dir = self.models_dir / model_name

        # Check if already downloaded
        if not force and self.get_model_path(model_name):
            return model_dir

        model_meta = SUPPORTED_MODELS[model_name]
        repo = model_meta["repo"]

        # Create model directory
        model_dir.mkdir(parents=True, exist_ok=True)

        try:
            for filename in model_meta["files"]:
                url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
                dest = model_dir / filename

                print(f"  Downloading {filename}...")
                self._download_file(url, dest)

            # Write metadata
            meta_file = model_dir / "aria_meta.json"
            meta_file.write_text(json.dumps({
                "name": model_name,
                "repo": repo,
                "params": model_meta["params"],
                "num_layers": model_meta["num_layers"],
                "hidden_dim": model_meta["hidden_dim"],
            }, indent=2))

            return model_dir

        except Exception as e:
            # Clean up partial download
            if model_dir.exists():
                shutil.rmtree(model_dir)
            raise ConnectionError(f"Failed to download {model_name}: {e}") from e

    def _download_file(self, url: str, dest: Path):
        """
        Download a single file from a URL.

        Args:
            url: Source URL
            dest: Destination file path
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": f"ARIA-Protocol/{__version__}"}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                with open(dest, "wb") as f:
                    shutil.copyfileobj(response, f)
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"HTTP {e.code} downloading {url}") from e
        except urllib.error.URLError as e:
            raise ConnectionError(f"Network error downloading {url}: {e}") from e

    def get_model_config(self, model_name: str) -> dict:
        """
        Get the configuration for a supported model.

        Args:
            model_name: Name of the model

        Returns:
            Model configuration dict

        Raises:
            ValueError: If model is not supported
        """
        if model_name not in SUPPORTED_MODELS:
            available = ", ".join(SUPPORTED_MODELS.keys())
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Supported models: {available}"
            )
        return SUPPORTED_MODELS[model_name].copy()

    @staticmethod
    def list_supported_models() -> Dict[str, dict]:
        """
        List all supported models (whether installed or not).

        Returns:
            Dict of model name -> model metadata
        """
        return SUPPORTED_MODELS.copy()

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a locally installed model.

        Args:
            model_name: Name of the model to delete

        Returns:
            True if deleted, False if not found
        """
        model_dir = self.models_dir / model_name
        if model_dir.exists():
            shutil.rmtree(model_dir)
            return True
        return False

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format byte size in human-readable format."""
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
