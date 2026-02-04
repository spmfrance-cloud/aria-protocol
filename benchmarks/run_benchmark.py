#!/usr/bin/env python3
"""
ARIA Protocol Benchmark Suite

Measures performance metrics for ARIA Protocol's 1-bit inference engine:
- Tokens per second (tokens/s)
- Energy per token (mJ/token)
- Latency percentiles (p50, p95, p99)
- RAM usage
- Comparison: simulation vs bitnet.cpp

MIT License - Anthony MURGO, 2026
"""

import argparse
import json
import os
import platform
import random
import resource
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aria.node import ARIANode
from aria.consent import ARIAConsent, TaskType
from aria.inference import InferenceEngine


# Default test prompts for reproducibility
DEFAULT_PROMPTS = [
    "What is the capital of France?",
    "Explain how photosynthesis works in simple terms.",
    "Write a Python function to calculate the factorial of a number.",
    "Compare and contrast renewable and non-renewable energy sources.",
    "Write a haiku about artificial intelligence.",
    "What are the main differences between Python and JavaScript?",
    "Describe the process of machine learning in three sentences.",
    "What is quantum computing and why is it important?",
    "Explain the concept of blockchain technology.",
    "How does the internet work at a high level?",
]


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark run."""
    iterations: int = 50
    max_tokens: int = 128
    seed: int = 42
    model: str = "aria-2b-1bit"
    warmup: int = 5
    tdp_watts: Optional[float] = None
    compare_bitnet: bool = False
    verbose: bool = False
    prompts: List[str] = None

    def __post_init__(self):
        if self.prompts is None:
            self.prompts = DEFAULT_PROMPTS


@dataclass
class BenchmarkResults:
    """Results from a benchmark run."""
    throughput_tokens_per_sec: float
    energy_mj_per_token: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    peak_ram_mb: float
    avg_ram_mb: float
    total_tokens: int
    total_time_sec: float
    latencies_ms: List[float]
    tokens_per_request: List[int]
    ram_samples_mb: List[float]


@dataclass
class EnvironmentInfo:
    """System environment information."""
    cpu: str
    cores: int
    ram_gb: float
    os: str
    os_version: str
    python: str
    aria_version: str


def get_cpu_info() -> str:
    """Get CPU model name."""
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        elif platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True
            )
            return result.stdout.strip()
    except Exception:
        pass
    return platform.processor() or "Unknown CPU"


def get_ram_gb() -> float:
    """Get total RAM in GB."""
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        return kb / (1024 * 1024)
        elif platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True
            )
            return int(result.stdout.strip()) / (1024**3)
    except Exception:
        pass
    return 0.0


def get_environment_info() -> EnvironmentInfo:
    """Collect environment information."""
    try:
        from aria import __version__ as aria_version
    except ImportError:
        aria_version = "0.2.5"

    return EnvironmentInfo(
        cpu=get_cpu_info(),
        cores=os.cpu_count() or 1,
        ram_gb=round(get_ram_gb(), 1),
        os=platform.system(),
        os_version=platform.release(),
        python=platform.python_version(),
        aria_version=aria_version,
    )


def get_git_commit() -> Optional[str]:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def estimate_tdp(cpu_name: str) -> float:
    """Estimate CPU TDP based on model name."""
    cpu_lower = cpu_name.lower()

    # Common TDP values (approximate)
    if "i9" in cpu_lower or "ryzen 9" in cpu_lower:
        return 125.0
    elif "i7" in cpu_lower or "ryzen 7" in cpu_lower:
        return 65.0
    elif "i5" in cpu_lower or "ryzen 5" in cpu_lower:
        return 65.0
    elif "i3" in cpu_lower or "ryzen 3" in cpu_lower:
        return 45.0
    elif "m1" in cpu_lower or "m2" in cpu_lower or "m3" in cpu_lower:
        return 20.0  # Apple Silicon is very efficient
    elif "arm" in cpu_lower or "aarch64" in cpu_lower:
        return 15.0
    else:
        return 65.0  # Default assumption


def get_current_ram_mb() -> float:
    """Get current process RAM usage in MB."""
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # maxrss is in KB on Linux, bytes on macOS
        if platform.system() == "Darwin":
            return usage.ru_maxrss / (1024 * 1024)
        return usage.ru_maxrss / 1024
    except Exception:
        return 0.0


def percentile(data: List[float], p: float) -> float:
    """Calculate percentile of data."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def check_bitnet_available() -> bool:
    """Check if bitnet.cpp is available."""
    try:
        result = subprocess.run(
            ["which", "bitnet"],
            capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


class ARIABenchmark:
    """ARIA Protocol benchmark runner."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.engine: Optional[InferenceEngine] = None
        self.node: Optional[ARIANode] = None

    def setup(self):
        """Initialize the inference engine."""
        # Set random seed for reproducibility
        random.seed(self.config.seed)

        # Create consent contract
        consent = ARIAConsent(
            cpu_percent=100,  # No limit for benchmarks
            max_ram_mb=4096,
            schedule="00:00-23:59",
            task_types=[TaskType.ANY],
        )

        # Create node (but don't start network)
        self.node = ARIANode(consent=consent, port=0)  # Port 0 = don't bind

        # Load model
        shard = self.node.load_model(
            model_id=self.config.model,
            num_layers=24,
            hidden_dim=2048,
            shard_start=0,
            shard_end=23
        )

        self.engine = self.node.engine

        if self.config.verbose:
            print(f"Loaded model: {self.config.model}")
            print(f"Shard: {shard.shard_id}")
            print(f"Layers: {shard.layer_start}-{shard.layer_end}")

    def warmup(self):
        """Run warmup iterations."""
        if self.config.verbose:
            print(f"\nRunning {self.config.warmup} warmup iterations...")

        prompt_idx = 0
        for i in range(self.config.warmup):
            prompt = self.config.prompts[prompt_idx % len(self.config.prompts)]
            self.engine.infer(
                query=prompt,
                model_id=self.config.model,
                max_tokens=self.config.max_tokens
            )
            prompt_idx += 1

    def run_simulation_benchmark(self) -> BenchmarkResults:
        """Run benchmark in simulation mode."""
        latencies_ms: List[float] = []
        tokens_per_request: List[int] = []
        ram_samples_mb: List[float] = []

        total_tokens = 0
        prompt_idx = 0

        if self.config.verbose:
            print(f"\nRunning {self.config.iterations} benchmark iterations...")

        start_time = time.perf_counter()

        for i in range(self.config.iterations):
            prompt = self.config.prompts[prompt_idx % len(self.config.prompts)]
            prompt_idx += 1

            # Measure single inference
            iter_start = time.perf_counter()

            result = self.engine.infer(
                query=prompt,
                model_id=self.config.model,
                max_tokens=self.config.max_tokens
            )

            iter_end = time.perf_counter()

            # Record metrics
            latency_ms = (iter_end - iter_start) * 1000
            latencies_ms.append(latency_ms)

            tokens = result.tokens_generated
            tokens_per_request.append(tokens)
            total_tokens += tokens

            # Sample RAM
            ram_mb = get_current_ram_mb()
            ram_samples_mb.append(ram_mb)

            if self.config.verbose and (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{self.config.iterations}")

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Calculate metrics
        throughput = total_tokens / total_time if total_time > 0 else 0

        # Energy estimation
        env = get_environment_info()
        tdp = self.config.tdp_watts or estimate_tdp(env.cpu)
        # Estimate CPU utilization during inference (assume 50% average)
        cpu_utilization = 0.5
        energy_joules = total_time * tdp * cpu_utilization
        energy_mj = energy_joules * 1000
        energy_per_token = energy_mj / total_tokens if total_tokens > 0 else 0

        return BenchmarkResults(
            throughput_tokens_per_sec=round(throughput, 2),
            energy_mj_per_token=round(energy_per_token, 2),
            latency_p50_ms=round(percentile(latencies_ms, 50), 2),
            latency_p95_ms=round(percentile(latencies_ms, 95), 2),
            latency_p99_ms=round(percentile(latencies_ms, 99), 2),
            peak_ram_mb=round(max(ram_samples_mb) if ram_samples_mb else 0, 1),
            avg_ram_mb=round(statistics.mean(ram_samples_mb) if ram_samples_mb else 0, 1),
            total_tokens=total_tokens,
            total_time_sec=round(total_time, 3),
            latencies_ms=[round(l, 2) for l in latencies_ms],
            tokens_per_request=tokens_per_request,
            ram_samples_mb=[round(r, 1) for r in ram_samples_mb],
        )

    def run_bitnet_benchmark(self) -> Optional[BenchmarkResults]:
        """Run benchmark with bitnet.cpp (if available)."""
        if not check_bitnet_available():
            return None

        # This would integrate with actual bitnet.cpp
        # For now, return None as it's not yet integrated
        if self.config.verbose:
            print("\nbitnet.cpp integration not yet available")

        return None

    def run(self) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        self.setup()
        self.warmup()

        env = get_environment_info()
        git_commit = get_git_commit()

        # Run simulation benchmark
        print("\n" + "=" * 60)
        print("ARIA Protocol Benchmark")
        print("=" * 60)
        print(f"Model: {self.config.model}")
        print(f"Iterations: {self.config.iterations}")
        print(f"Max Tokens: {self.config.max_tokens}")
        print(f"Seed: {self.config.seed}")

        sim_results = self.run_simulation_benchmark()

        # Print results
        print("\n" + "-" * 60)
        print("Performance Metrics (Simulation Mode)")
        print("-" * 60)
        print(f"  Throughput:     {sim_results.throughput_tokens_per_sec} tokens/s")
        print(f"  Energy:         {sim_results.energy_mj_per_token} mJ/token")
        print()
        print("Latency:")
        print(f"  p50:            {sim_results.latency_p50_ms} ms")
        print(f"  p95:            {sim_results.latency_p95_ms} ms")
        print(f"  p99:            {sim_results.latency_p99_ms} ms")
        print()
        print("Memory:")
        print(f"  Peak RAM:       {sim_results.peak_ram_mb} MB")
        print(f"  Avg RAM:        {sim_results.avg_ram_mb} MB")

        # Run bitnet comparison if requested
        bitnet_results = None
        if self.config.compare_bitnet:
            bitnet_results = self.run_bitnet_benchmark()
            if bitnet_results:
                print()
                print("-" * 60)
                print("Comparison: Simulation vs bitnet.cpp")
                print("-" * 60)
                speedup = bitnet_results.throughput_tokens_per_sec / sim_results.throughput_tokens_per_sec
                print(f"  Simulation:     {sim_results.throughput_tokens_per_sec} tokens/s")
                print(f"  bitnet.cpp:     {bitnet_results.throughput_tokens_per_sec} tokens/s")
                print(f"  Speedup:        {speedup:.2f}x")

        # Compile full report
        report = {
            "meta": {
                "version": env.aria_version,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "git_commit": git_commit,
                "seed": self.config.seed,
            },
            "environment": asdict(env),
            "config": {
                "model": self.config.model,
                "iterations": self.config.iterations,
                "max_tokens": self.config.max_tokens,
                "warmup": self.config.warmup,
                "tdp_watts": self.config.tdp_watts or estimate_tdp(env.cpu),
            },
            "results": {
                "simulation": {
                    "throughput_tokens_per_sec": sim_results.throughput_tokens_per_sec,
                    "energy_mj_per_token": sim_results.energy_mj_per_token,
                    "latency_p50_ms": sim_results.latency_p50_ms,
                    "latency_p95_ms": sim_results.latency_p95_ms,
                    "latency_p99_ms": sim_results.latency_p99_ms,
                    "peak_ram_mb": sim_results.peak_ram_mb,
                    "avg_ram_mb": sim_results.avg_ram_mb,
                    "total_tokens": sim_results.total_tokens,
                    "total_time_sec": sim_results.total_time_sec,
                },
            },
            "raw_data": {
                "simulation": {
                    "latencies_ms": sim_results.latencies_ms,
                    "tokens_per_request": sim_results.tokens_per_request,
                    "ram_samples_mb": sim_results.ram_samples_mb,
                }
            },
        }

        if bitnet_results:
            report["results"]["bitnet"] = {
                "throughput_tokens_per_sec": bitnet_results.throughput_tokens_per_sec,
                "energy_mj_per_token": bitnet_results.energy_mj_per_token,
                "latency_p50_ms": bitnet_results.latency_p50_ms,
                "latency_p95_ms": bitnet_results.latency_p95_ms,
                "latency_p99_ms": bitnet_results.latency_p99_ms,
                "peak_ram_mb": bitnet_results.peak_ram_mb,
                "avg_ram_mb": bitnet_results.avg_ram_mb,
            }
            report["raw_data"]["bitnet"] = {
                "latencies_ms": bitnet_results.latencies_ms,
                "tokens_per_request": bitnet_results.tokens_per_request,
            }

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ARIA Protocol Benchmark Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_benchmark.py
  python run_benchmark.py --iterations 100 --max-tokens 256
  python run_benchmark.py --seed 123 --output results/my_benchmark.json
  python run_benchmark.py --compare-bitnet --verbose
        """
    )

    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=50,
        help="Number of inference iterations (default: 50)"
    )
    parser.add_argument(
        "--max-tokens", "-t",
        type=int,
        default=128,
        help="Maximum tokens per inference (default: 128)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="aria-2b-1bit",
        help="Model ID to benchmark (default: aria-2b-1bit)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output JSON file path (default: benchmarks/results/benchmark_<timestamp>.json)"
    )
    parser.add_argument(
        "--warmup", "-w",
        type=int,
        default=5,
        help="Warmup iterations (default: 5)"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default=None,
        help="Custom prompts file (JSON array)"
    )
    parser.add_argument(
        "--tdp",
        type=float,
        default=None,
        help="CPU TDP in watts for energy estimation (default: auto-detect)"
    )
    parser.add_argument(
        "--compare-bitnet",
        action="store_true",
        help="Compare with bitnet.cpp if available"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable detailed output"
    )

    args = parser.parse_args()

    # Load custom prompts if specified
    prompts = None
    if args.prompts:
        try:
            with open(args.prompts) as f:
                prompts = json.load(f)
        except Exception as e:
            print(f"Error loading prompts file: {e}")
            return 1

    # Create config
    config = BenchmarkConfig(
        iterations=args.iterations,
        max_tokens=args.max_tokens,
        seed=args.seed,
        model=args.model,
        warmup=args.warmup,
        tdp_watts=args.tdp,
        compare_bitnet=args.compare_bitnet,
        verbose=args.verbose,
        prompts=prompts,
    )

    # Run benchmark
    benchmark = ARIABenchmark(config)
    report = benchmark.run()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"benchmark_{timestamp}.json"

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write results
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 60)
    print(f"Results saved to: {output_path}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
