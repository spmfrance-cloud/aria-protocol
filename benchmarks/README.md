# ARIA Protocol Benchmarks

Performance benchmarking suite for ARIA Protocol inference operations.

## Latest Results — v0.5.5 Ecosystem Benchmark

**9 models, 3 vendors, 6 tiers, 170 test runs** on AMD Ryzen 9 7845HX (12C/24T, Zen 4, 64 GB DDR5), Clang 20.1.8, AVX-512 VNNI+VBMI.

### Throughput Summary (8 threads, 256 tokens, median of 5 runs)

| Model | Params | Source | Type | tok/s | Energy* |
|-------|--------|--------|------|-------|---------|
| BitNet-b1.58-large | 0.7B | Microsoft | Post-quantized | **118.25** | ~15 mJ/tok |
| Falcon-E-1B-Instruct | 1.0B | TII | **Native 1-bit** | **80.19** | ~23 mJ/tok |
| Falcon3-1B-Instruct | 1.0B | TII | Post-quantized | 56.31 | ~33 mJ/tok |
| BitNet-b1.58-2B-4T | 2.4B | Microsoft | Native 1-bit | 37.76 | ~49 mJ/tok |
| Falcon-E-3B-Instruct | 3.0B | TII | **Native 1-bit** | **49.80** | ~37 mJ/tok |
| Falcon3-3B-Instruct | 3.0B | TII | Post-quantized | 33.21 | ~55 mJ/tok |
| Falcon3-7B-Instruct | 7.0B | TII | Post-quantized | 19.89 | ~92 mJ/tok |
| Llama3-8B-1.58 | 8.0B | Microsoft | Post-quantized | 16.97 | ~108 mJ/tok |
| Falcon3-10B-Instruct | 10.0B | TII | Post-quantized | 15.12 | ~121 mJ/tok |

### Native vs Post-Quantized

| Scale | Native (Falcon-E) | Post-Quantized (Falcon3) | Advantage |
|-------|-------------------|--------------------------|-----------|
| 1B | 80.19 tok/s | 56.31 tok/s | **+42%** |
| 3B | 49.80 tok/s | 33.21 tok/s | **+50%** |

Models natively trained in 1-bit consistently outperform post-training quantized equivalents.

*Energy estimated via CPU-time × TDP/threads. Full data: [`results/benchmark_v055_ecosystem.json`](results/benchmark_v055_ecosystem.json)

---

## Overview

This benchmark suite measures key performance metrics for ARIA Protocol's 1-bit inference engine, including:

- **Throughput**: Tokens generated per second (tokens/s)
- **Energy Efficiency**: Estimated energy consumption per token (mJ/token)
- **Latency**: Response time percentiles (p50, p95, p99)
- **Memory Usage**: Peak RAM consumption during inference
- **Comparison**: Simulation mode vs bitnet.cpp (when available)

## Before You Benchmark

**Critical:** Read the full [Reproduction Guide](REPRODUCING.md) before running benchmarks. Key verification steps:

1. **Check AVX-512 status** — Run `./llama-cli --version` and verify
   `AVX512 = 1` in system_info. If `AVX512 = 0`, your build silently
   fell back to AVX2 and results will be significantly slower.

2. **Use 8 threads** — 1-bit inference is memory-bound, not compute-bound.
   More threads causes cache contention and *reduces* performance
   (documented: -11.6% at 24 threads on Ryzen 9 7845HX).

3. **Warmup first** — Especially on laptop CPUs, run 500+ warmup tokens
   before timing to avoid Turbo Boost frequency ramp-up artifacts.

4. **Sanity check** — Larger models MUST be slower than smaller models.
   Any inversion indicates a build or configuration problem.

## Methodology

### Test Environment

Benchmarks are designed to be reproducible across different hardware configurations. Each run captures:

- Hardware specs (CPU model, cores, RAM)
- OS and Python version
- ARIA Protocol version
- Timestamp and git commit hash

### Reproducibility

All benchmarks use:

- **Fixed random seed**: Default seed `42` for deterministic behavior
- **Standard prompt set**: Predefined test prompts covering various use cases
- **Configurable parameters**: All settings exposed via CLI flags
- **JSON output**: Machine-readable results for CI/CD integration

### Metrics Collection

#### Tokens per Second (tokens/s)

```
tokens/s = total_tokens_generated / total_inference_time_seconds
```

Measured across multiple iterations to account for variance.

#### Energy per Token (mJ/token)

Estimated using the formula:
```
energy_mj = cpu_time_seconds * tdp_watts * 1000 / tokens_generated
```

Where TDP is estimated based on CPU model or provided as a parameter.

#### Latency Percentiles

- **p50**: Median latency (50th percentile)
- **p95**: 95th percentile latency
- **p99**: 99th percentile latency (optional)

Computed from individual request latencies across all iterations.

#### RAM Usage

Peak resident set size (RSS) measured during inference using `resource.getrusage()` on Unix systems or `psutil` when available.

## Prefill vs Decode Performance

Our benchmarks report both metrics separately:

| Metric | Description | Typical Use |
|--------|-------------|-------------|
| **Prompt eval (prefill)** | Processing the input prompt | Measures context ingestion speed |
| **Token generation (decode)** | Generating new tokens | Critical metric for interactive use |

In our results:
- `prompt_tokens_per_sec`: Prefill throughput
- `tokens_per_sec` / `generation_tokens_per_sec`: Decode throughput

For latency-sensitive applications (chatbots, real-time), **decode speed** is the key metric.
For batch processing (summarization, analysis), **prefill speed** matters more.

## Energy Measurement Limitations

Energy consumption (`mJ/token`) is **estimated**, not directly measured. The calculation uses:

```
energy_per_token = (cpu_time * TDP_watts) / tokens_generated * 1000
```

**Important caveats:**

- TDP (Thermal Design Power) is a maximum rating, not actual consumption
- Real power draw varies with workload, temperature, and CPU state
- We assume 100% CPU utilization during inference (conservative estimate)
- No direct power measurement via RAPL, external meters, or GPU power APIs

**How to improve accuracy:**

- Use `--tdp <watts>` to specify your actual CPU TDP
- For precise measurements, use external power meters or platform RAPL interfaces
- Compare relative values (same hardware) rather than absolute values

**Why we still report it:**

Despite limitations, estimated energy provides:
- Reproducible comparisons across runs
- Relative efficiency metrics between models/configurations
- A baseline for future direct measurement integration

We welcome contributions to add direct power measurement support.

## Running Benchmarks

### Quick Start

```bash
# Run default benchmark suite
python benchmarks/run_benchmark.py

# Run with specific configuration
python benchmarks/run_benchmark.py \
  --iterations 100 \
  --max-tokens 256 \
  --seed 42 \
  --output benchmarks/results/my_benchmark.json
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--iterations` | Number of inference iterations | 50 |
| `--max-tokens` | Maximum tokens per inference | 128 |
| `--seed` | Random seed for reproducibility | 42 |
| `--model` | Model ID to benchmark | aria-2b-1bit |
| `--output` | Output JSON file path | benchmarks/results/benchmark_<timestamp>.json |
| `--warmup` | Warmup iterations (not counted) | 5 |
| `--prompts` | Custom prompts file (JSON array) | built-in |
| `--tdp` | CPU TDP in watts for energy estimation | auto-detect |
| `--compare-bitnet` | Compare with bitnet.cpp if available | false |
| `--verbose` | Enable detailed output | false |

### Example Output

```
ARIA Protocol Benchmark Results
==============================
Model: aria-2b-1bit
Iterations: 100
Max Tokens: 128

Performance Metrics:
  Throughput:     42.5 tokens/s
  Energy:         28.3 mJ/token

Latency:
  p50:            23.5 ms
  p95:            45.2 ms
  p99:            67.8 ms

Memory:
  Peak RAM:       412 MB
  Avg RAM:        385 MB

Comparison (if bitnet.cpp available):
  Simulation:     42.5 tokens/s
  bitnet.cpp:     156.2 tokens/s
  Speedup:        3.67x
```

## Standard Test Prompts

The benchmark uses a standard set of prompts to ensure comparability:

1. **Short factual**: "What is the capital of France?"
2. **Medium explanation**: "Explain how photosynthesis works in simple terms."
3. **Code generation**: "Write a Python function to calculate factorial."
4. **Long reasoning**: "Compare and contrast renewable and non-renewable energy sources."
5. **Creative**: "Write a haiku about artificial intelligence."

Custom prompts can be provided via a JSON file:

```json
[
  "Your custom prompt 1",
  "Your custom prompt 2"
]
```

## Results Directory

Benchmark results are stored in `benchmarks/results/` as JSON files:

```
benchmarks/results/
├── benchmark_20260201_120000.json
├── benchmark_20260201_140000.json
└── ...
```

### Result Schema

```json
{
  "meta": {
    "version": "0.2.5",
    "timestamp": "2026-02-01T12:00:00Z",
    "git_commit": "abc123",
    "seed": 42
  },
  "environment": {
    "cpu": "AMD Ryzen 9 7845HX",
    "cores": 12,
    "ram_gb": 32,
    "os": "Linux 5.15",
    "python": "3.11.0"
  },
  "config": {
    "model": "aria-2b-1bit",
    "iterations": 100,
    "max_tokens": 128,
    "warmup": 5
  },
  "results": {
    "throughput_tokens_per_sec": 42.5,
    "energy_mj_per_token": 28.3,
    "latency_p50_ms": 23.5,
    "latency_p95_ms": 45.2,
    "latency_p99_ms": 67.8,
    "peak_ram_mb": 412,
    "avg_ram_mb": 385
  },
  "raw_data": {
    "latencies_ms": [22.1, 24.3, ...],
    "tokens_generated": [128, 127, ...]
  }
}
```

## Interpreting Results

### Expected Performance Ranges

For ARIA Protocol v0.2.5 on typical consumer hardware:

| Metric | Simulation Mode | With bitnet.cpp |
|--------|-----------------|-----------------|
| Throughput | 30-60 tokens/s | 100-200 tokens/s |
| Energy | 25-40 mJ/token | 15-30 mJ/token |
| p50 Latency | 20-50 ms | 5-20 ms |
| RAM Usage | 300-500 MB | 300-500 MB |

### Factors Affecting Performance

1. **SIMD Level (AVX-512 vs AVX2)**: Verify `AVX512 = 1` in system_info.
   A silent fallback to AVX2 halves SIMD width with no warning.
2. **L1 Cache Load Bandwidth**: The bottleneck for 1-bit inference. CPUs
   with native 512-bit L1 load paths (128 bytes/cycle) outperform those
   using double-pumped 256-bit paths (64 bytes/cycle per core).
3. **CCD Topology (AMD)**: Multi-CCD CPUs incur ~68ns cross-CCD latency.
   Thread pinning to a single CCD may improve performance.
4. **Memory Bandwidth (DRAM)**: DDR5-5600 (~83 GB/s) vs DDR4-3200
   (~51 GB/s) affects multi-threaded scaling ceiling.
5. **Thermal Throttling**: Laptop CPUs throttle under sustained load.
   Monitor frequency during benchmarks.
6. **Turbo Boost Inertia**: Lightweight models may not trigger max Turbo
   on laptop CPUs, causing paradoxical slowdowns vs heavier models.
7. **Background Processes**: Ensure minimal system load for accurate results.

## CI/CD Integration

Benchmarks can be integrated into CI pipelines:

```yaml
# Example GitHub Actions workflow
benchmark:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Run benchmarks
      run: |
        python benchmarks/run_benchmark.py \
          --iterations 20 \
          --output benchmarks/results/ci_benchmark.json
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: benchmarks/results/
```

## Note on Output Quality

These benchmarks focus on **systems performance** (throughput, latency, energy). They do not measure output quality (perplexity, accuracy, coherence).

Output quality is assumed comparable when:
- Using the same model weights
- Using identical generation parameters (temperature, top_p, etc.)
- Using the same quantization format (I2_S)

For quality benchmarks, refer to the original model publications (e.g., [Microsoft BitNet b1.58 Technical Report](https://huggingface.co/papers/2504.12285)).

## Contributing

When adding new benchmarks:

1. Ensure reproducibility with fixed seeds
2. Document the metric calculation method
3. Add appropriate error handling
4. Update this README with new options

## License

MIT License - See [LICENSE](../LICENSE) for details.
