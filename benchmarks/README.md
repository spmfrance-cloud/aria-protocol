# ARIA Protocol Benchmarks

Performance benchmarking suite for ARIA Protocol inference operations.

## Overview

This benchmark suite measures key performance metrics for ARIA Protocol's 1-bit inference engine, including:

- **Throughput**: Tokens generated per second (tokens/s)
- **Energy Efficiency**: Estimated energy consumption per token (mJ/token)
- **Latency**: Response time percentiles (p50, p95, p99)
- **Memory Usage**: Peak RAM consumption during inference
- **Comparison**: Simulation mode vs bitnet.cpp (when available)

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
    "cpu": "Intel Core i7-12700",
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

1. **CPU Architecture**: AVX2/AVX-512 support significantly improves performance
2. **Memory Bandwidth**: Affects model loading and activation transfer
3. **Thermal Throttling**: Extended benchmarks may show degradation
4. **Background Processes**: Ensure minimal system load for accurate results

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

## Contributing

When adding new benchmarks:

1. Ensure reproducibility with fixed seeds
2. Document the metric calculation method
3. Add appropriate error handling
4. Update this README with new options

## License

MIT License - See [LICENSE](../LICENSE) for details.
