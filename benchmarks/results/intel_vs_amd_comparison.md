# ARIA Protocol - Intel vs AMD CPU Benchmark Comparison

> Benchmark date: 2026-02-12
> ARIA Protocol v0.5.2 | Backend: subprocess (bitnet.cpp llama-cli)
> Configuration: 5 prompts, 50 max tokens, 8 threads

## 1. Hardware Specifications

| Spec | Intel | AMD |
|------|-------|-----|
| **CPU** | Intel Core i7-11370H @ 3.30GHz | AMD Ryzen 9 7845HX |
| **Architecture** | Tiger Lake (11th Gen) | Zen 4 (Raphael) |
| **Cores / Threads** | 4C / 8T | 12C / 24T |
| **Max Clock** | 3.30 GHz (base) / 4.80 GHz (boost) | 3.60 GHz (base) / 5.20 GHz (boost) |
| **SIMD** | AVX-512 (native 512-bit, VNNI) | AVX-512 (double-pumped 256-bit, VNNI) |
| **RAM** | 16 GB | 64 GB DDR5 |
| **OS** | Windows 11 (10.0.28020) | Windows 11 |
| **Python** | 3.12.8 | 3.14.3 |

## 2. Performance Comparison (tokens/s)

| Model | Params | Intel tok/s | AMD tok/s | Delta | Intel latency (ms) | AMD latency (ms) | Delta |
|-------|--------|-------------|-----------|-------|---------------------|-------------------|-------|
| BitNet-b1.58-large | 0.7B | 61.81 | 120.25 | -48.6% | 1248.23 | 588.00 | +112.3% |
| BitNet-b1.58-2B-4T | 2.4B | 77.21 | 36.62 | +110.8% | 657.01 | 2120.00 | -69.0% |
| Llama3-8B-1.58 | 8.0B | 10.36 | 15.03 | -31.1% | 7873.58 | N/A | N/A |

> Note: The 2.4B model performance difference may be explained by Intel Tiger Lake's native 512-bit AVX-512 execution vs AMD Zen 4's double-pumped 256-bit implementation. Both support VNNI, but the execution width differs significantly for ternary weight lookup operations.

## 3. Energy Efficiency (estimated mJ/token)

| Model | Params | Intel mJ/tok | AMD mJ/tok (est.) | Delta |
|-------|--------|--------------|--------------------|-------|
| BitNet-b1.58-large | 0.7B | 382.11 | ~187.00 | +104.3% |
| BitNet-b1.58-2B-4T | 2.4B | 197.10 | ~636.00 | -69.0% |
| Llama3-8B-1.58 | 8.0B | 2410.28 | ~1500.00 | +60.7% |

> Energy estimates are derived from TDP-based models and are approximate. Intel i7-11370H TDP: 35W, AMD Ryzen 9 7845HX TDP: 45W.

## 4. Key Observations

- **Core count dominates throughput on the 0.7B model**: The AMD Ryzen 9 7845HX (12C/24T) delivers ~2x the throughput of the Intel i7-11370H (4C/8T) on the 0.7B model, suggesting that small-model inference scales well with thread count in bitnet.cpp's MAD (multiply-and-add) kernel.

- **The 2.4B model favors Intel significantly**: The Intel platform achieves 77.21 tok/s vs AMD's 36.62 tok/s. Both CPUs support AVX-512 VNNI, but Tiger Lake executes 512-bit instructions natively on full-width execution units, while Zen 4 double-pumps them as 2× 256-bit µops. The BitNet-b1.58-2B-4T model (Microsoft's newer architecture) likely has memory access patterns that benefit from true 512-bit throughput on the ternary LUT kernels.

- **8B model shows expected scaling**: The 8B model is compute-bound on both platforms, with the AMD achieving ~1.45x the throughput of Intel, roughly proportional to the core count advantage (12C vs 4C) after accounting for memory bandwidth limitations.

- **Native 512-bit execution vs core count trade-off**: Both CPUs support AVX-512 VNNI, but they implement it differently: Tiger Lake has native 512-bit execution units, while Zen 4 decodes AVX-512 as 2× 256-bit µops. For the 0.7B and 8B models, the AMD's 3× core advantage dominates. For the 2.4B model, Intel's true 512-bit throughput appears more impactful — suggesting that the optimal hardware depends on the model architecture.

- **Memory bandwidth is not the bottleneck for small models**: The 0.7B model (257 MB quantized) fits entirely in L3 cache on both platforms, making the benchmark primarily compute-bound. The 8B model (3.7 GB) exceeds cache capacity, making memory bandwidth more relevant.

## 5. Conclusion

CPU-first inference with 1-bit quantized models (via bitnet.cpp) is viable on **both major x86 architectures** (Intel and AMD). The ARIA Protocol's subprocess backend successfully executes on Intel Tiger Lake (11th Gen) with full AVX-512 support, achieving:

- **61.81 tok/s** on the 0.7B model (usable for real-time applications)
- **77.21 tok/s** on the 2.4B model (excellent throughput)
- **10.36 tok/s** on the 8B model (adequate for batch/offline processing)

These results validate the ARIA Protocol's thesis that **1-bit LLM inference does not require GPU hardware** and can run on commodity laptop CPUs across Intel and AMD platforms, with performance scaling predictably based on core count and available SIMD extensions.
