# Reproducing ARIA Protocol Benchmarks

This guide helps you reproduce the benchmark results published in our [Benchmark Report](../docs/benchmark-report.md). Following these steps ensures accurate, comparable results.

## Prerequisites

- ARIA Protocol installed (`pip install -e ".[dev]"`)
- bitnet.cpp compiled for your CPU architecture
- At least one BitNet model downloaded (`aria model download BitNet-b1.58-2B-4T`)

## Critical: Verify Your Build BEFORE Benchmarking

### Step 1 — Check AVX-512 Status

bitnet.cpp uses compile-time SIMD detection. If AVX-512 flags are not set, the binary **silently falls back to AVX2** (256-bit), halving SIMD width with no warning message.

Run your binary and check system_info output:

```bash
./llama-cli --version
```

Or look for this line during inference:

```
AVX512 = 1   ← CORRECT: AVX-512 is active
AVX512 = 0   ← WARNING: Fallen back to AVX2, rebuild required!
```

### Step 2 — Verify Compilation Flags

For AMD Zen 4 (Ryzen 7000 series):

```bash
cmake -DGGML_AVX512=ON -DGGML_AVX512_VBMI=ON -DGGML_AVX512_VNNI=ON \
      -DCMAKE_CXX_FLAGS="-march=znver4" ..
```

For Intel Tiger Lake (11th gen):

```bash
cmake -DGGML_AVX512=ON -DGGML_AVX512_VBMI=ON -DGGML_AVX512_VNNI=ON \
      -DCMAKE_CXX_FLAGS="-march=tigerlake" ..
```

**Important**: Both AMD Zen 4 and Intel Tiger Lake support the full AVX-512 instruction set including VNNI, VBMI, and BITALG. The performance difference between these architectures comes from L1 data cache load bandwidth (native 512-bit paths on Tiger Lake vs double-pumped 256-bit on Zen 4), not from missing instruction support.

### Step 3 — Sanity Check Your Results

Before publishing any results, verify:

- **Larger models MUST be slower than smaller models** on the same hardware. If your 2.4B model runs faster than 0.7B, something is wrong (see [Troubleshooting](#troubleshooting) below).
- **8 threads should be near-optimal** for most CPUs. If 24 threads is significantly faster than 8, your build may be using AVX2 instead of AVX-512.

## Benchmark Commands

### Basic Benchmark

```bash
python benchmarks/run_benchmark.py --prompts 5 --output results.json
```

### Thread Scaling Test

```bash
for t in 4 8 12; do
    python benchmarks/run_benchmark.py --threads $t \
        --prompts 5 --output results_${t}t.json
done
```

### With Specific TDP (for energy estimation)

```bash
# AMD Ryzen 9 7845HX: 45W (mobile) or 54W (sustained)
python benchmarks/run_benchmark.py --tdp 54 --output results.json

# Intel i7-11370H: 35W
python benchmarks/run_benchmark.py --tdp 35 --output results.json
```

## Understanding Thread Scaling

1-bit LLM inference using LUT kernels is memory-bound, not compute-bound. The hot loop (`ggml_vec_dot_i2_i8_s`) spends ~80% of CPU time streaming weight data from cache. This has critical implications:

| Threads | Expected Behavior |
|---------|-------------------|
| 4 | Good baseline performance |
| 6-8 | Optimal zone — memory bandwidth saturated |
| 12+ | Diminishing returns or degradation due to cache contention |
| All cores | Often slower than 8 threads (documented: -11.6% at 24T on Ryzen 9 7845HX) |

**Rule: more threads ≠ better performance for 1-bit inference.**

Adding threads beyond the memory bandwidth saturation point causes cache contention and increases synchronization overhead. This is a physical limitation, not a software bug.

## Platform-Specific Notes

### AMD Multi-CCD CPUs (Ryzen 9 7000+ series)

Ryzen 9 processors with 8+ cores typically use 2 CCDs (Core Complex Dies) connected via Infinity Fabric through the I/O die. Cross-CCD communication adds ~68ns latency compared to ~27ns intra-CCD.

When using 8 threads, they are distributed across both CCDs, forcing cross-CCD synchronization on every token. For advanced testing, you can pin threads to a single CCD:

```bash
# Linux: pin to first 6 cores (CCD 0)
taskset -c 0-5 ./llama-cli -m model.gguf -t 6 -p "prompt"

# Windows: pin to first 6 cores
start /affinity 0x3F llama-cli.exe -m model.gguf -t 6 -p "prompt"
```

We are actively investigating whether 6 threads on a single CCD outperforms 8 threads across both CCDs for this workload.

### Laptop CPUs (H-series / Mobile)

Laptop CPUs with aggressive power management (Intel H-series, AMD HS/HX) may exhibit **Turbo Boost inertia**:

- **Problem**: Lightweight models (0.7B) may complete inference passes so quickly that the CPU never ramps to full Turbo frequency. Heavier models (2.4B+) sustain load long enough to trigger maximum boost. This can cause paradoxical results where larger models appear faster.
- **Fix**:
  1. Set power plan to **High Performance** (not Balanced)
  2. Run a warmup of **500+ generated tokens** before starting the timed benchmark
  3. Run all models in the same session with warmup between each

## Energy Estimation

ARIA's energy measurements are estimates based on:

```
Energy (J) = inference_time (s) × TDP (W) × estimated_utilization
```

This is **NOT** direct power measurement. For accurate energy data, RAPL (Running Average Power Limit) integration is planned for a future release. Always disclose this methodology when comparing energy figures.

## Troubleshooting

### "My 2.4B model is faster than my 0.7B model"

This is physically impossible under normal conditions. Check:

1. AVX-512 status (`AVX512 = 1` in system_info) for **BOTH** models
2. Power plan set to **High Performance** (not Balanced/Power Saver)
3. Warmup was run before timing
4. Both models use the same quantization format (I2_S)

### "My results are much slower than published"

Check:

1. `AVX512 = 0` in system_info → rebuild with correct flags
2. Running on battery power → plug in and set High Performance
3. Background processes consuming CPU/memory → close other applications
4. Thermal throttling on laptop → ensure adequate cooling

### "Thread scaling shows no improvement beyond 4 threads"

This is expected and correct for 1-bit inference. The workload saturates memory bandwidth early. The published optimal is 8 threads, but your specific CPU may peak at 4-6 depending on cache hierarchy and memory speed.

### "Cross-architecture comparison shows unexpected gaps"

Ensure:

1. SAME SIMD level on both machines (both AVX-512, or both AVX2)
2. Same thread count for per-thread comparison
3. Same model, same prompt, same token count
4. Both machines at full performance (no throttling, no battery mode)

## Reference Results

Our published results (AMD Ryzen 9 7845HX, AVX-512, 8 threads):

| Model | Params | tok/s | Energy (mJ/token) |
|-------|--------|-------|--------------------|
| BitNet-b1.58-large | 0.7B | 89.65 | ~11 |
| BitNet-b1.58-2B-4T | 2.4B | 36.94 | ~28 |
| Llama3-8B-1.58 | 8.0B | 15.03 | ~66 |

**Known issue**: Our Intel i7-11370H results are under review due to a suspected Turbo Boost anomaly. Updated results will be published after re-benchmarking with the corrected protocol described above.

## Contributing Benchmark Results

If you run benchmarks on different hardware and want to contribute:

1. Follow this guide completely (especially the verification steps)
2. Include `system_info` output showing AVX-512 status
3. Include your CPU model, thread count, power plan, and OS
4. Submit via GitHub issue with your JSON results attached
5. We'll add verified community results to the benchmark report

---

For the full benchmark methodology and analysis, see [docs/benchmark-report.md](../docs/benchmark-report.md).
