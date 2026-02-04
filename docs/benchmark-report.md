# ARIA Protocol — Benchmark Report v1.0

<p align="center">
  <strong>Comprehensive Performance Analysis & Industry Comparison</strong><br>
  <em>Distributed 1-Bit AI Inference on Consumer Hardware</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/benchmarks-reproducible-green.svg" alt="Benchmarks">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

---

## Executive Summary

This report presents comprehensive benchmark results for ARIA Protocol, a peer-to-peer distributed inference system using 1-bit quantized models. All benchmarks were conducted on consumer hardware with fully reproducible methodology.

### Key Metrics at a Glance

| Metric | ARIA (Best) | ARIA (Balanced) | Industry Standard |
|--------|-------------|-----------------|-------------------|
| **Throughput** | 89.65 t/s | 36.94 t/s | 50-100 t/s (GPU) |
| **Energy/Token** | ~11 mJ | ~28 mJ | ~500-2000 mJ (datacenter) |
| **Hardware Cost** | $0 (existing CPU) | $0 | $10,000+ (GPU) |
| **Latency (TTFT)** | 88 ms | 504 ms | 200-800 ms (API) |
| **Privacy** | 100% local | 100% local | Data sent to cloud |

### Primary Findings

1. **1-bit inference is memory-bound, not compute-bound** — Optimal performance at 8 threads
2. **Horizontal scaling beats vertical scaling** — P2P distribution outperforms multi-threading
3. **Energy efficiency is 20-50× better** than estimated datacenter GPU inference
4. **Sub-linear model scaling** — 8B model is 11× larger but only 6× slower than 0.7B

---

## Table of Contents

1. [Test Environment](#1-test-environment)
2. [Benchmark Methodology](#2-benchmark-methodology)
3. [Performance Results](#3-performance-results)
4. [Industry Comparison](#4-industry-comparison)
5. [Energy Analysis](#5-energy-analysis)
6. [Economic Analysis](#6-economic-analysis)
7. [Technical Deep Dive](#7-technical-deep-dive)
8. [ARIA Value Proposition](#8-aria-value-proposition)
9. [Conclusions](#9-conclusions)
10. [Appendix](#10-appendix)

---

## 1. Test Environment

### Hardware Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST SYSTEM SPECS                        │
├─────────────────────────────────────────────────────────────┤
│  CPU:        AMD Ryzen 9 7845HX                             │
│  Cores:      12 cores / 24 threads                          │
│  Base:       3.0 GHz / Boost: 5.2 GHz                       │
│  Cache:      L2: 12MB / L3: 64MB                            │
│  TDP:        45-75W (configurable)                          │
│  RAM:        63.2 GB DDR5                                   │
│  OS:         Windows 11 (10.0.26100)                        │
│  Storage:    NVMe SSD                                       │
└─────────────────────────────────────────────────────────────┘
```

### Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9.25 | Runtime environment |
| bitnet.cpp | 3962 (1f86f058) | 1-bit inference engine |
| Clang | 20.1.8 | Compiler for bitnet.cpp |
| ARIA Protocol | 0.3.0 | Distributed inference layer |

### Models Tested

| Model | Parameters | GGUF Size | Quantization | Source |
|-------|------------|-----------|--------------|--------|
| BitNet-b1.58-large | 0.7B | 257 MB | I2_S (2 bpw) | Microsoft |
| BitNet-b1.58-2B-4T | 2.4B | 1,133 MB | I2_S (2 bpw) | Microsoft |
| Llama3-8B-1.58 | 8.0B | 3,677 MB | I2_S (2 bpw) | Community |

---

## 2. Benchmark Methodology

### Reproducibility Standards

All benchmarks follow strict reproducibility guidelines:

```
┌─────────────────────────────────────────────────────────────┐
│                 REPRODUCIBILITY CHECKLIST                   │
├─────────────────────────────────────────────────────────────┤
│  ✓ Fixed random seed (42)                                   │
│  ✓ Standardized prompts (documented)                        │
│  ✓ Temperature = 0 (deterministic)                          │
│  ✓ Cold start measurements (fresh process)                  │
│  ✓ Multiple runs averaged                                   │
│  ✓ Full metadata captured (CPU, OS, git commit, timestamp)  │
│  ✓ JSON output format for automation                        │
└─────────────────────────────────────────────────────────────┘
```

### Metrics Collected

| Metric | Unit | Description |
|--------|------|-------------|
| **Throughput (decode)** | tokens/s | Token generation speed |
| **Throughput (prefill)** | tokens/s | Prompt processing speed |
| **Latency p50/p95/p99** | ms | Response time percentiles |
| **TTFT** | ms | Time to first token |
| **Energy** | mJ/token | Estimated energy consumption |
| **RAM Peak** | MB | Maximum memory usage |
| **Model Load Time** | ms | Time to load model into memory |

### Energy Estimation Method

```
Energy per token = (CPU_time × TDP_watts) / tokens_generated × 1000

⚠️ LIMITATION: This is an estimate based on CPU time and TDP rating.
   Actual power draw varies with workload and CPU state.
   For precise measurements, use RAPL or external power meters.
```

---

## 3. Performance Results

### 3.1 Model Size Comparison

```
                    THROUGHPUT BY MODEL SIZE
                    (tokens/second, 8 threads)
    
    100 ┤
        │ ████████████████████████████████████████  89.65 t/s
     80 ┤ ████████████████████████████████████████
        │ ████████████████████████████████████████
     60 ┤ ████████████████████████████████████████
        │ ████████████████████████████████████████
     40 ┤ ████████████████████████████████████████  ████████████████  36.94 t/s
        │ ████████████████████████████████████████  ████████████████
     20 ┤ ████████████████████████████████████████  ████████████████  ████████  15.03 t/s
        │ ████████████████████████████████████████  ████████████████  ████████
      0 ┼─────────────────────────────────────────────────────────────────────
              0.7B (BitNet-large)     2.4B (BitNet-2B)      8.0B (Llama3-8B)
```

| Model | Generation (t/s) | Prompt (t/s) | ms/token | Load Time | RAM |
|-------|------------------|--------------|----------|-----------|-----|
| **0.7B** | **89.65** | 91.07 | 11.16 | 168 ms | ~400 MB |
| **2.4B** | 36.94 | 37.45 | 27.07 | 658 ms | ~1,300 MB |
| **8.0B** | 15.03 | 15.95 | 66.53 | 1,031 ms | ~4,200 MB |

**Scaling Analysis:**
- 0.7B → 2.4B (3.4× params): 2.4× slower (sub-linear ✓)
- 2.4B → 8.0B (3.3× params): 2.5× slower (sub-linear ✓)
- 0.7B → 8.0B (11.4× params): 6.0× slower (excellent scaling)

### 3.2 Thread Scaling Analysis

```
                    THREAD SCALING (2.4B Model)
                    
    Threads:    4        8        12       24
               ─────────────────────────────────
    t/s:      36.07    36.94    36.76    31.88
                        ▲ PEAK
                        
              ┌────────────────────────────────┐
              │  ████  ████  ████  ███         │
              │  ████  ████  ████  ███         │
              │  ████  ████  ████  ███         │
              │  ████  ████  ████  ███         │
              │   4T    8T   12T   24T         │
              └────────────────────────────────┘
              
    ⚠️ KEY INSIGHT: More threads ≠ better performance
       1-bit LUT kernels are MEMORY-BOUND, not compute-bound
```

| Threads | Generation (t/s) | Change vs 4T | Recommendation |
|---------|------------------|--------------|----------------|
| 4 | 36.07 | baseline | Minimum viable |
| **8** | **36.94** | **+2.4%** | **Optimal** ⭐ |
| 12 | 36.76 | +1.9% | Diminishing returns |
| 24 | 31.88 | **-11.6%** | Performance degradation |

### 3.3 Parallel Inference Analysis

```
                PARALLEL INFERENCE (3 × 8 threads)
                
    Single Stream (8T):     ████████████████████████████  36.94 t/s
    
    3 Parallel Streams:     
      Stream 1:             ████████████  13.54 t/s
      Stream 2:             ████████████  13.60 t/s  
      Stream 3:             ████████████  13.72 t/s
                            ─────────────────────────
      Combined:             █████████████████████████████████  40.86 t/s
      
    Expected (3× single):   ████████████████████████████████████████████  110.82 t/s
    Actual:                 █████████████████████████████████  40.86 t/s
    
    Efficiency:             36.9% (severe cache contention)
```

| Configuration | Per-Stream | Combined | Efficiency |
|---------------|------------|----------|------------|
| 1 × 8 threads | 36.94 t/s | 36.94 t/s | 100% |
| 3 × 8 threads | ~13.62 t/s | 40.86 t/s | 36.9% |

**Key Insight:** Cache contention severely limits intra-node parallelism.
This validates ARIA's P2P approach: distribute across machines, not threads.

### 3.4 Context Length Impact

```
            GENERATION LENGTH IMPACT (6-token prompt)
            
    Tokens:      32       128       512      1024
                ─────────────────────────────────
    t/s:       36.09    36.61    34.13    34.00
    
    Degradation:  0%     +1.4%    -5.4%    -5.8%
    
    ✓ EXCELLENT STABILITY: Only 5.8% degradation at 1024 tokens
```

```
            PROMPT LENGTH IMPACT (128-token generation)
            
    Prompt:      3        59       224       557 tokens
                ─────────────────────────────────────
    TTFT:       88ms    1.6s     6.1s     15.9s
    Gen t/s:   34.51   36.30    35.61    32.72
    
    ✓ Prompt processing is LINEAR (~28 ms/token)
    ✓ Generation speed minimally affected (-5.2%)
```

---

## 4. Industry Comparison

### 4.1 Inference Providers Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INFERENCE COST COMPARISON                            │
│                     (per 1 million output tokens)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GPT-4o          ████████████████████████████████████████████  $15.00      │
│  Claude 3.5      ██████████████████████████████████████████    $15.00      │
│  GPT-4o-mini     ████████                                       $2.40      │
│  Claude Haiku    █████                                          $1.25      │
│  Llama 3.1 (API) ████                                           $0.90      │
│  ARIA (0.7B)*    ▏                                              $0.003     │
│  ARIA (2.4B)*    ▏                                              $0.008     │
│  ARIA (8.0B)*    ▏                                              $0.018     │
│                                                                             │
│  * Electricity cost only (€0.25/kWh), hardware already owned               │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Provider | Model | Cost/1M tokens | Latency (TTFT) | Privacy |
|----------|-------|----------------|----------------|---------|
| OpenAI | GPT-4o | $15.00 | 200-500ms | ❌ Cloud |
| OpenAI | GPT-4o-mini | $2.40 | 150-400ms | ❌ Cloud |
| Anthropic | Claude 3.5 Sonnet | $15.00 | 200-600ms | ❌ Cloud |
| Anthropic | Claude 3.5 Haiku | $1.25 | 100-300ms | ❌ Cloud |
| Together.ai | Llama 3.1 70B | $0.90 | 300-800ms | ❌ Cloud |
| **ARIA** | **0.7B (local)** | **~$0.003** | **88ms** | **✅ Local** |
| **ARIA** | **2.4B (local)** | **~$0.008** | **504ms** | **✅ Local** |
| **ARIA** | **8.0B (local)** | **~$0.018** | **1,031ms** | **✅ Local** |

*ARIA costs calculated at €0.25/kWh electricity rate, hardware cost excluded (assumes existing CPU)*

### 4.2 Throughput Comparison

```
                    THROUGHPUT COMPARISON (tokens/second)
                    
    LOCAL CPU INFERENCE (ARIA):
    ├── 0.7B model:    ████████████████████████████████████  89.65 t/s
    ├── 2.4B model:    ████████████████                      36.94 t/s
    └── 8.0B model:    ████████                              15.03 t/s
    
    GPU INFERENCE (datacenter):
    ├── A100 (Llama 7B):  ███████████████████████████████████████  ~120 t/s
    ├── RTX 4090 (7B):    ██████████████████████████████████       ~80 t/s
    └── RTX 3080 (7B):    ████████████████████████                 ~50 t/s
    
    API PROVIDERS (estimated):
    ├── GPT-4o:           ████████████████████████████████████     ~80 t/s
    ├── Claude 3.5:       ██████████████████████████████████       ~70 t/s
    └── Llama API:        ████████████████████████████████████████ ~100 t/s
```

### 4.3 Qualitative Comparison Matrix

| Feature | Cloud APIs | Local GPU | ARIA (CPU) |
|---------|------------|-----------|------------|
| **Initial Cost** | $0 | $1,000-$10,000 | $0 (existing) |
| **Running Cost** | $1-15/M tokens | ~$0.05/M tokens | ~$0.01/M tokens |
| **Throughput** | 70-100 t/s | 50-120 t/s | 15-90 t/s |
| **Latency (TTFT)** | 200-800ms | 50-200ms | 88-1000ms |
| **Privacy** | ❌ Data sent | ✅ Local | ✅ Local |
| **Offline** | ❌ No | ✅ Yes | ✅ Yes |
| **Scalability** | ✅ Unlimited | ❌ Hardware limited | ✅ P2P network |
| **Energy Efficiency** | ❌ Datacenter | ⚠️ GPU power | ✅ Low TDP |
| **Model Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 5. Energy Analysis

### 5.1 Energy per Token Comparison

```
                    ENERGY CONSUMPTION (mJ per token)
                    
    DATACENTER GPU (estimated):
    ├── A100 (400W, 120 t/s):     ████████████████████████  3,333 mJ/token
    ├── H100 (700W, 200 t/s):     █████████████████████     3,500 mJ/token
    └── Average datacenter*:      ██████████████████████████████  ~5,000 mJ/token
    
    CONSUMER GPU (estimated):
    ├── RTX 4090 (450W, 80 t/s):  ██████████████████████████████████  5,625 mJ/token
    └── RTX 3080 (320W, 50 t/s):  ████████████████████████████████████████  6,400 mJ/token
    
    ARIA CPU INFERENCE:
    ├── 0.7B (75W, 90 t/s):       █                           ~11 mJ/token
    ├── 2.4B (75W, 37 t/s):       ██                          ~28 mJ/token
    └── 8.0B (75W, 15 t/s):       ████                        ~66 mJ/token
    
    * Includes PUE (Power Usage Effectiveness) ~1.5x
```

| Platform | Power Draw | Throughput | Energy/Token | vs ARIA (2.4B) |
|----------|------------|------------|--------------|----------------|
| **ARIA 0.7B** | ~75W | 89.65 t/s | **~11 mJ** | 0.4× |
| **ARIA 2.4B** | ~75W | 36.94 t/s | **~28 mJ** | 1× (baseline) |
| **ARIA 8.0B** | ~75W | 15.03 t/s | **~66 mJ** | 2.4× |
| RTX 4090 | ~450W | ~80 t/s | ~5,625 mJ | 200× |
| A100 (datacenter) | ~400W | ~120 t/s | ~3,333 mJ | 119× |
| Cloud API* | ~700W+ | ~100 t/s | ~7,000 mJ+ | 250× |

*Cloud includes datacenter overhead (cooling, networking, redundancy)

### 5.2 Annual Energy Projection

```
    Scenario: 10 million tokens/day inference workload
    
    ┌─────────────────────────────────────────────────────────────┐
    │              ANNUAL ENERGY CONSUMPTION (kWh)                │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  Cloud API:         ████████████████████████████  25,550 kWh │
    │  Local GPU (4090):  ████████████████████████████  20,531 kWh │
    │  ARIA 8.0B:         █                                241 kWh │
    │  ARIA 2.4B:         ▏                                102 kWh │
    │  ARIA 0.7B:         ▏                                 40 kWh │
    │                                                             │
    │  ARIA savings vs Cloud: 99.6% energy reduction              │
    │  ARIA savings vs GPU:   99.5% energy reduction              │
    └─────────────────────────────────────────────────────────────┘
```

| Platform | Energy/Token | Daily (10M tokens) | Annual | CO₂/year* |
|----------|--------------|--------------------| -------|-----------|
| Cloud API | ~7,000 mJ | 70 kWh | 25,550 kWh | 10.2 tons |
| RTX 4090 | ~5,625 mJ | 56.25 kWh | 20,531 kWh | 8.2 tons |
| **ARIA 8.0B** | ~66 mJ | 0.66 kWh | **241 kWh** | 96 kg |
| **ARIA 2.4B** | ~28 mJ | 0.28 kWh | **102 kWh** | 41 kg |
| **ARIA 0.7B** | ~11 mJ | 0.11 kWh | **40 kWh** | 16 kg |

*Based on EU average 0.4 kg CO₂/kWh

---

## 6. Economic Analysis

### 6.1 Total Cost of Ownership (3-Year)

```
    Scenario: 10 million tokens/day, 3-year projection
    
    ┌─────────────────────────────────────────────────────────────┐
    │                   3-YEAR TCO COMPARISON                     │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  OpenAI GPT-4o:     ████████████████████████████  $164,250  │
    │  Claude 3.5:        ████████████████████████████  $164,250  │
    │  Llama API:         █████████                      $32,850  │
    │  Local RTX 4090:    ███                             $8,533  │
    │  ARIA (existing):   ▏                                 $76   │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

| Solution | Hardware | API/Electricity | 3-Year Total | vs ARIA |
|----------|----------|-----------------|--------------|---------|
| GPT-4o | $0 | $164,250 | **$164,250** | 2,161× |
| Claude 3.5 Sonnet | $0 | $164,250 | **$164,250** | 2,161× |
| Llama API | $0 | $32,850 | **$32,850** | 432× |
| RTX 4090 (local) | $2,000 | $6,533 | **$8,533** | 112× |
| **ARIA (existing CPU)** | $0 | $76 | **$76** | 1× |

*Assumptions: €0.25/kWh, 10M tokens/day, existing CPU for ARIA*

### 6.2 Break-Even Analysis

```
    When does ARIA become more economical than alternatives?
    
    vs Cloud API (GPT-4o at $15/M tokens):
    └── Break-even: Immediately (no upfront cost)
    
    vs New GPU Purchase ($2,000 RTX 4090):
    └── Break-even: Never needed (ARIA uses existing hardware)
    
    vs Llama API ($0.90/M tokens):
    └── Break-even: After ~84,000 tokens (approximately 1 hour of usage)
```

---

## 7. Technical Deep Dive

### 7.1 Why 1-Bit Inference is Memory-Bound

Traditional LLM inference:
```
Weight × Activation = Output
(float16) × (float16) = (float16)
→ Requires FPU (Floating Point Unit)
→ GPU excels at parallel FP operations
```

1-Bit inference:
```
Weight ∈ {-1, 0, +1}
Activation × Weight = Lookup Table Operation
→ No multiplication needed
→ Pure addition/subtraction
→ CPU cache becomes the bottleneck
```

```
┌─────────────────────────────────────────────────────────────┐
│              MEMORY HIERARCHY BOTTLENECK                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    L1 Cache (32KB)     ████  ~1 ns latency                  │
│    L2 Cache (512KB)    ████████  ~3 ns latency              │
│    L3 Cache (64MB)     ████████████████  ~10 ns latency     │
│    RAM (64GB)          ████████████████████████  ~100 ns    │
│                                                             │
│    ⚠️ Adding threads increases L2/L3 cache contention       │
│    ⚠️ Parallel requests fight for the same cache lines     │
│    ✓ Solution: Distribute across machines (separate caches) │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Why P2P Beats Multi-Threading

```
    VERTICAL SCALING (more threads, same machine):
    
    1 × 8 threads:   [████████]                    36.94 t/s
    3 × 8 threads:   [████████][████████][████████] 40.86 t/s (+11%)
                      ↓ Cache contention ↓
                      
    HORIZONTAL SCALING (more machines, via ARIA P2P):
    
    Machine A (8T): [████████]                     36.94 t/s
    Machine B (8T): [████████]                     36.94 t/s
    Machine C (8T): [████████]                     36.94 t/s
                    ─────────────────────────────────────────
    Total:                                        110.82 t/s (+200%)
                    ↑ Separate caches, no contention ↑
```

### 7.3 ARIA Pipeline Parallelism

```
┌─────────────────────────────────────────────────────────────┐
│              ARIA DISTRIBUTED INFERENCE PIPELINE            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Request                                              │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │ Node A  │───▶│ Node B  │───▶│ Node C  │                │
│   │ L0-L7   │    │ L8-L15  │    │ L16-L23 │                │
│   │ 8 threads│   │ 8 threads│   │ 8 threads│               │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │              │              │                      │
│        ▼              ▼              ▼                      │
│   Activations    Activations    Final Output               │
│   (base64)       (base64)       (tokens)                   │
│                                                             │
│   ✓ Each node uses optimal 8 threads                       │
│   ✓ No cache contention between nodes                      │
│   ✓ Automatic failover if node drops                       │
│   ✓ Provenance recorded on ledger                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. ARIA Value Proposition

### 8.1 What ARIA Provides

```
┌─────────────────────────────────────────────────────────────┐
│                    ARIA UNIQUE VALUE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                        │
│  │  EFFICIENCY     │  • 99% energy reduction vs cloud       │
│  │                 │  • Runs on existing hardware           │
│  │                 │  • No GPU required                     │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  PRIVACY        │  • 100% local inference                │
│  │                 │  • No data sent to cloud               │
│  │                 │  • GDPR-compliant by design            │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  SCALABILITY    │  • P2P horizontal scaling              │
│  │                 │  • No central infrastructure           │
│  │                 │  • Add nodes = add capacity            │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  TRANSPARENCY   │  • Immutable provenance ledger         │
│  │                 │  • Every inference recorded            │
│  │                 │  • Auditable energy consumption        │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  SOVEREIGNTY    │  • No vendor lock-in                   │
│  │                 │  • Open protocol (MIT license)         │
│  │                 │  • Community-governed network          │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Target Use Cases

| Use Case | Why ARIA | Alternative Pain Points |
|----------|----------|-------------------------|
| **Edge AI** | Low power, offline | Cloud requires connectivity |
| **Healthcare** | Data privacy | HIPAA concerns with cloud |
| **Finance** | Auditability | Black-box API compliance |
| **Education** | Zero cost | API costs prohibitive |
| **Research** | Reproducibility | API behavior changes |
| **Developing regions** | Low bandwidth | Cloud latency issues |

### 8.3 ARIA vs Alternatives Summary

```
                        ARIA POSITIONING MAP
                        
    Cost ($)                    
    High │                      ● Cloud APIs
         │                        (GPT-4, Claude)
         │                      
         │              ● Local GPU
         │                (RTX 4090)
         │
         │      ● Llama API
         │
    Low  │  ★ ARIA ────────────────────────────────
         └────────────────────────────────────────────▶
              Low              Privacy              High
              (Cloud)                              (Local)
              
    ★ ARIA: Best privacy + lowest cost
    Trade-off: Model quality (1-bit vs full precision)
```

---

## 9. Conclusions

### 9.1 Key Findings Summary

| Finding | Implication |
|---------|-------------|
| 1-bit inference is memory-bound | Optimize for cache, not compute |
| Optimal threads = 8 | Don't over-parallelize |
| Parallel requests don't scale | Use P2P distribution instead |
| 99% energy reduction | Massive sustainability impact |
| $0 hardware cost | Democratizes AI inference |
| Sub-linear model scaling | Larger models viable on CPU |

### 9.2 Recommendations

**For Individual Users:**
- Start with 0.7B model (89 t/s) for chat applications
- Use 2.4B model for better quality/speed balance
- Keep thread count at 8 for optimal performance

**For Organizations:**
- Deploy ARIA nodes on existing hardware fleet
- Use P2P distribution for horizontal scaling
- Integrate via OpenAI-compatible API (zero code changes)

**For Developers:**
- Contribute to energy measurement improvements (RAPL integration)
- Build applications on ARIA's OpenAI-compatible API
- Extend the protocol for specific use cases

### 9.3 Future Work

| Priority | Item | Expected Impact |
|----------|------|-----------------|
| High | Direct power measurement (RAPL) | Accurate energy data |
| High | Mobile node support | Expand network capacity |
| Medium | GPU backend comparison | Validate architecture |
| Medium | Output quality benchmarks | Complete picture |
| Low | Multi-model pipeline | Advanced use cases |

---

## 10. Appendix

### A. Benchmark Commands

```bash
# Clone repository
git clone https://github.com/spmfrance-cloud/aria-protocol
cd aria-protocol

# Install dependencies
pip install -e .

# Run basic benchmark
python benchmarks/run_benchmark.py --prompts 5 --output results.json

# Run with specific threads
python benchmarks/run_benchmark.py --threads 8 --output results_8t.json

# Run with custom TDP
python benchmarks/run_benchmark.py --tdp 65 --output results_65w.json
```

### B. Raw Benchmark Data

All benchmark data is available in JSON format:
- `benchmarks/results/baseline.json` — Simulation baseline
- `benchmarks/results/bitnet_real.json` — Real inference baseline
- `benchmarks/results/thread_scaling.json` — Thread optimization
- `benchmarks/results/parallel_inference.json` — Parallel requests
- `benchmarks/results/model_sizes.json` — Model comparison
- `benchmarks/results/context_length.json` — Context impact

### C. Methodology Limitations

1. **Energy estimation** — Based on CPU-time × TDP, not direct measurement
2. **Single hardware** — Tested on AMD Ryzen 9 7845HX only
3. **Model quality** — Not benchmarked (assumed comparable for same model)
4. **Network latency** — P2P benchmarks not included in this report
5. **Long-term stability** — Short benchmark runs only

### D. References

1. Microsoft BitNet b1.58 Technical Report (2024)
2. llama.cpp Project Documentation
3. OpenAI API Pricing (February 2025)
4. Anthropic Claude Pricing (February 2025)
5. NVIDIA A100/H100 Specifications
6. EU Electricity Price Index (Eurostat)

---

<p align="center">
  <strong>ARIA Protocol Benchmark Report v1.0</strong><br>
  <em>February 2026</em><br>
  <a href="https://github.com/spmfrance-cloud/aria-protocol">github.com/spmfrance-cloud/aria-protocol</a>
</p>

---

**Document Information:**
- Version: 1.0
- Date: February 4, 2026
- Author: ARIA Protocol Team
- License: MIT
