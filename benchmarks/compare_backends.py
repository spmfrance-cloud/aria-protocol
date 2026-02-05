"""
ARIA Protocol - Backend Comparison Benchmark

Compares inference performance across all available backends:
- native: ctypes bindings to bitnet.cpp DLL
- subprocess: llama-cli.exe subprocess
- simulation: reference implementation (no real inference)

Usage:
    python benchmarks/compare_backends.py [--prompts N] [--max-tokens N] [--output FILE]

MIT License - Anthony MURGO, 2026
"""

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure aria package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ---------------------------------------------------------------------------
# Test prompts
# ---------------------------------------------------------------------------

TEST_PROMPTS = [
    "What is artificial intelligence?",
    "Explain quantum computing in simple terms.",
    "Write a Python function to sort a list.",
    "What are the benefits of renewable energy?",
    "Describe the architecture of a neural network.",
]

# ---------------------------------------------------------------------------
# Backend detection helpers
# ---------------------------------------------------------------------------


def _detect_native():
    """Try to instantiate BitNetNative and check availability."""
    try:
        from aria.bitnet_native import BitNetNative
        instance = BitNetNative()
        return instance if instance.is_native else None
    except Exception:
        return None


def _detect_subprocess(threads: int):
    """Try to instantiate BitNetSubprocess and check availability."""
    try:
        from aria.bitnet_subprocess import BitNetSubprocess
        instance = BitNetSubprocess(threads=threads)
        return instance if instance.is_available else None
    except Exception:
        return None


def _get_simulation_engine(model_id: str):
    """Return an InferenceEngine in simulation mode."""
    from aria.inference import InferenceEngine
    engine = InferenceEngine(node_id="benchmark", backend="simulation")
    engine.load_model(model_id)
    return engine


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


def run_backend_benchmark(backend_name, run_fn, prompts, max_tokens):
    """
    Run a series of prompts through *run_fn* and collect metrics.

    *run_fn(prompt, max_tokens)* must return a dict with at least:
        tokens_per_second, latency_ms, energy_estimate_mj,
        energy_mj_per_token, output_length
    """
    results = []
    for prompt in prompts:
        try:
            metrics = run_fn(prompt, max_tokens)
            metrics["prompt"] = prompt
            metrics["status"] = "ok"
        except Exception as exc:
            metrics = {
                "prompt": prompt,
                "status": "error",
                "error": str(exc),
                "tokens_per_second": 0,
                "latency_ms": 0,
                "energy_estimate_mj": 0,
                "energy_mj_per_token": 0,
                "output_length": 0,
            }
        results.append(metrics)
    return results


# ---------------------------------------------------------------------------
# Per-backend run functions
# ---------------------------------------------------------------------------


def _make_native_fn(native_instance, model_id):
    """Build a run function for the native backend."""
    # Attempt to load model (will raise on failure)
    native_instance.load_model(model_id, auto_download=False)

    def _run(prompt, max_tokens):
        start = time.time()
        output = native_instance.generate(prompt, max_tokens=max_tokens)
        elapsed_ms = (time.time() - start) * 1000
        tokens_generated = max_tokens  # approximate
        tps = tokens_generated / (elapsed_ms / 1000) if elapsed_ms > 0 else 0
        energy_mj = 28.0  # baseline estimate for native
        return {
            "tokens_per_second": round(tps, 2),
            "latency_ms": round(elapsed_ms, 2),
            "energy_estimate_mj": round(energy_mj, 2),
            "energy_mj_per_token": round(energy_mj / max(tokens_generated, 1), 4),
            "output_length": len(output),
        }
    return _run


def _make_subprocess_fn(subprocess_instance, model_id):
    """Build a run function for the subprocess backend."""
    def _run(prompt, max_tokens):
        result = subprocess_instance.run_inference(
            prompt=prompt,
            model_id=model_id,
            max_tokens=max_tokens,
        )
        if result.get("error"):
            raise RuntimeError(result["error"])
        tokens_generated = result.get("tokens_generated", max_tokens)
        return {
            "tokens_per_second": result.get("tokens_per_second", 0),
            "latency_ms": result.get("time_ms", 0),
            "energy_estimate_mj": result.get("energy_estimate_mj", 0),
            "energy_mj_per_token": result.get("energy_mj_per_token", 0),
            "output_length": len(result.get("output", "")),
        }
    return _run


def _make_simulation_fn(engine, model_id):
    """Build a run function for the simulation backend."""
    def _run(prompt, max_tokens):
        start = time.time()
        res = engine.infer(query=prompt, model_id=model_id, max_tokens=max_tokens)
        elapsed_ms = (time.time() - start) * 1000
        return {
            "tokens_per_second": float("inf"),
            "latency_ms": round(elapsed_ms, 2),
            "energy_estimate_mj": round(res.energy_mj, 2),
            "energy_mj_per_token": round(res.energy_mj / max(res.tokens_generated, 1), 4),
            "output_length": len(res.output_text),
        }
    return _run


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _avg(values):
    return sum(values) / len(values) if values else 0


def print_summary(all_results, model_id, num_prompts, max_tokens):
    """Print a formatted comparison table to stdout."""
    print()
    print("ARIA Backend Comparison Benchmark")
    print("\u2550" * 58)
    print(f"Model: {model_id} | Prompts: {num_prompts} | Max tokens: {max_tokens}")
    print(f"{'Backend':<17}{'Avg tok/s':>10}{'Avg latency':>14}{'Avg energy':>13}   Status")
    print("\u2500" * 58)

    for backend_name, results in all_results.items():
        ok = [r for r in results if r["status"] == "ok"]
        if not ok:
            print(f"{backend_name:<17}{'-':>10}{'-':>14}{'-':>13}   unavailable")
            continue

        avg_tps = _avg([r["tokens_per_second"] for r in ok])
        avg_lat = _avg([r["latency_ms"] for r in ok])
        avg_nrg = _avg([r["energy_estimate_mj"] for r in ok])

        if avg_tps == float("inf"):
            tps_str = "\u221e"
        else:
            tps_str = f"{avg_tps:.2f}"

        if avg_lat < 1:
            lat_str = "<1 ms"
        else:
            lat_str = f"{avg_lat:.2f} ms"

        nrg_str = f"{avg_nrg:.2f} mJ"
        status = "\u2713 (reference)" if backend_name == "simulation" else "\u2713"

        print(f"{backend_name:<17}{tps_str:>10}{lat_str:>14}{nrg_str:>13}   {status}")

    print()


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------


def build_json_report(all_results, model_id, num_prompts, max_tokens, threads):
    """Build a JSON-serialisable report dict."""
    return {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "platform": platform.platform(),
            "cpu": platform.processor() or platform.machine(),
            "threads": threads,
            "python_version": platform.python_version(),
        },
        "model": model_id,
        "num_prompts": num_prompts,
        "max_tokens": max_tokens,
        "results": {
            backend: [
                {k: (None if v == float("inf") else v) for k, v in r.items()}
                for r in results
            ]
            for backend, results in all_results.items()
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def create_parser():
    parser = argparse.ArgumentParser(
        prog="compare_backends",
        description="ARIA Protocol - Backend Comparison Benchmark",
    )
    parser.add_argument(
        "--prompts", type=int, default=3,
        help="Number of prompts to test (default: 3)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=50,
        help="Max tokens per inference (default: 50)",
    )
    parser.add_argument(
        "--threads", type=int, default=8,
        help="CPU threads for subprocess backend (default: 8)",
    )
    parser.add_argument(
        "--output", type=str,
        default=str(Path(__file__).resolve().parent / "results" / "backend_comparison.json"),
        help="JSON output file (default: benchmarks/results/backend_comparison.json)",
    )
    parser.add_argument(
        "--model", type=str, default="bitnet-b1.58-large",
        help="Model to benchmark (default: bitnet-b1.58-large)",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    prompts = TEST_PROMPTS[: args.prompts]
    model_id = args.model

    print("ARIA Backend Comparison Benchmark")
    print("=" * 58)
    print(f"Model: {model_id}")
    print(f"Prompts: {len(prompts)} | Max tokens: {args.max_tokens} | Threads: {args.threads}")
    print()

    # ------------------------------------------------------------------
    # Detect available backends
    # ------------------------------------------------------------------
    all_results = {}

    # 1. Native
    print("Detecting native backend...", end=" ", flush=True)
    native = _detect_native()
    if native:
        print("available")
        try:
            fn = _make_native_fn(native, model_id)
            print(f"  Running {len(prompts)} prompts on native backend...")
            all_results["native"] = run_backend_benchmark("native", fn, prompts, args.max_tokens)
        except Exception as exc:
            print(f"  Skipped (model load failed: {exc})")
            all_results["native"] = [{"status": "error", "error": str(exc)}]
    else:
        print("unavailable")
        all_results["native"] = []

    # 2. Subprocess
    print("Detecting subprocess backend...", end=" ", flush=True)
    sub = _detect_subprocess(args.threads)
    if sub:
        print(f"available ({sub.exe_path})")
        try:
            fn = _make_subprocess_fn(sub, model_id)
            print(f"  Running {len(prompts)} prompts on subprocess backend...")
            all_results["subprocess"] = run_backend_benchmark("subprocess", fn, prompts, args.max_tokens)
        except Exception as exc:
            print(f"  Skipped ({exc})")
            all_results["subprocess"] = [{"status": "error", "error": str(exc)}]
    else:
        print("unavailable")
        all_results["subprocess"] = []

    # 3. Simulation (always available)
    print("Detecting simulation backend... available")
    engine = _get_simulation_engine(model_id)
    fn = _make_simulation_fn(engine, model_id)
    print(f"  Running {len(prompts)} prompts on simulation backend...")
    all_results["simulation"] = run_backend_benchmark("simulation", fn, prompts, args.max_tokens)

    # ------------------------------------------------------------------
    # Display summary
    # ------------------------------------------------------------------
    print_summary(all_results, model_id, len(prompts), args.max_tokens)

    # ------------------------------------------------------------------
    # Save JSON report
    # ------------------------------------------------------------------
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = build_json_report(all_results, model_id, len(prompts), args.max_tokens, args.threads)
    output_path.write_text(json.dumps(report, indent=2))
    print(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
