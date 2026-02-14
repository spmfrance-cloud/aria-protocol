# ARIA Protocol

[![Version](https://img.shields.io/badge/version-0.5.5-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-orange.svg)]()
[![Tests](https://img.shields.io/badge/tests-196%20passing-brightgreen.svg)]()
[![Benchmarks](https://img.shields.io/badge/benchmarks-reproducible-blue.svg)]()
[![Desktop](https://img.shields.io/badge/desktop-Windows%20%7C%20macOS%20%7C%20Linux-purple.svg)]()

**Autonomous Responsible Intelligence Architecture**

> A peer-to-peer protocol for efficient, ethical, and decentralized AI inference.

## What is ARIA?

ARIA is an open protocol that enables distributed AI inference across consumer devices. By combining **1-bit model inference**, **peer-to-peer networking**, and **blockchain provenance**, ARIA creates a decentralized AI network that is:

- **70-82% more energy efficient** than GPU-based systems
- **Runs on any CPU** (no expensive hardware required)
- **Fully transparent** with immutable inference records
- **Consent-based** - no resource used without permission
* **Extensible model ecosystem** — 8+ organizations producing 1-bit models independently (Microsoft, TII, MBZUAI, ETH Zurich, HuggingFace...)

---

## Quick Start

### Installation

```bash
pip install aria-protocol
```

### Start a Node

```bash
# Start an ARIA node
aria node start --port 8765 --model aria-2b-1bit

# Start the API server
aria api start --port 3000

# Test inference
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "aria-2b-1bit", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Use with OpenAI Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="aria"
)

response = client.chat.completions.create(
    model="aria-2b-1bit",
    messages=[{"role": "user", "content": "What is quantum computing?"}]
)

print(response.choices[0].message.content)
```

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| **P2P Network** | Real WebSocket-based peer-to-peer communication | ✅ Complete |
| **1-Bit Inference** | Ternary weight models (-1, 0, +1) for CPU efficiency | ✅ Complete |
| **Pipeline Parallelism** | Distribute model layers across multiple nodes | ✅ Complete |
| **OpenAI-Compatible API** | Drop-in replacement for OpenAI API | ✅ Complete |
| **Web Dashboard** | Real-time monitoring with WebSocket updates | ✅ Complete |
| **CLI Interface** | Full command-line control of nodes | ✅ Complete |
| **Provenance Ledger** | Blockchain for inference traceability | ✅ Complete |
| **Proof of Useful Work** | Every computation is real AI inference (no wasted work) | ✅ Complete |
| **Proof of Sobriety** | Verifiable energy efficiency attestations | ✅ Complete |
| **Consent Contracts** | Explicit resource usage permissions | ✅ Complete |
| **bitnet.cpp Integration** | Real 1-bit inference kernels | ✅ Complete |
| **Native BitNet** | Python ctypes bindings to bitnet.cpp | ✅ Complete |
| **Subprocess Backend** | llama-cli process-based inference | ✅ Complete |
| **Model Manager** | Auto-download models from HuggingFace | ✅ Complete |

### Coming in v0.6.0+

| Feature | Description | Target |
|---------|-------------|--------|
| **Kademlia DHT** | Decentralized peer discovery replacing bootstrap servers | v0.6.0 |
| **NAT Traversal** | STUN/TURN for nodes behind routers | v0.6.0 |
| **Desktop ↔ Backend Bridge** | Live inference from desktop app via Python backend | v0.6.0 |
| **Consensus Inference** | Multi-agent orchestrated inference across network nodes | v0.7.0 |
| **KV-Cache NVMe Paging** | Extended context (500K+ tokens) via SSD offloading | v0.7.0–v0.8.0 |
| **5/5 Cognitive Memory** | Full human memory model: episodic, semantic, procedural, working, and prospective (deferred intentions with time/semantic/condition triggers) | v0.7.0 |
| **Knowledge Network** | Distributed RAG via P2P embedding sharing | v0.8.0 |
| **ARIA-LM** | Community-evolving language model via SAPO + LoRA merging | v0.9.0 |

---

## Benchmarks

### v0.5.5 — Complete 1-bit ecosystem benchmark (latest)

First comprehensive multi-vendor 1-bit model benchmark. 9 models from 3 sources, 6 testing tiers, 170 test runs. All tests on identical hardware, same build, same day.

**Hardware:** AMD Ryzen 9 7845HX (12C/24T, Zen 4, 64 GB DDR5)
**Build:** bitnet.cpp + Clang 20.1.8, AVX-512 VNNI+VBMI enabled
**Protocol:** 8 threads, 256 tokens, 5 runs per model, median selected

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

> **Key finding — Native vs post-quantized:** Models natively trained in 1-bit (Falcon-E)
> outperform post-training quantized models by **+42% at 1B** and **+50% at 3B**.
> This validates the importance of native ternary training over post-hoc quantization.

Key findings:
- **Thread scaling**: All models peak at 6-8 threads; 1-bit inference is memory-bound, not compute-bound
- **CCD topology**: Smaller models benefit from single-CCD pinning; 7B+ models show minimal CCD sensitivity
- **Sustained throughput**: Performance remains stable across generation lengths (32-2048 tokens)
- **10B on CPU**: Falcon3-10B at 15 tok/s demonstrates viable interactive inference on consumer hardware

*Energy is estimated via CPU-time x TDP/threads — not a direct hardware measurement. See [benchmark methodology](./benchmarks/README.md) for details.

Full 6-tier results: [`benchmarks/results/benchmark_v055_ecosystem.json`](./benchmarks/results/benchmark_v055_ecosystem.json)

### Total Cost of Ownership (3 years, 10M tokens/day)

| Solution | Hardware | Running Costs | Total (3y) | vs ARIA |
|----------|----------|---------------|------------|---------|
| Cloud APIs (frontier) | $0 | $164,250 | $164,250 | 2,161x |
| Llama API | $0 | $32,850 | $32,850 | 432x |
| RTX 4090 (local) | $2,000 | $6,533 | $8,533 | 112x |
| **ARIA Protocol (CPU)** | **$0** | **$76** | **$76** | **1x** |

*Assumptions: existing CPU hardware, electricity at $0.25/kWh.*

All benchmarks are reproducible:
```bash
pip install -e .

# v0.5.2 comparative benchmark (requires bitnet.cpp build)
python benchmarks/compare_backends.py --prompts 5 --max-tokens 50 --threads 8 --output results.json

# v0.3.0 direct benchmark
python benchmarks/run_benchmark.py --prompts 5 --output results.json
```

Full results: [`benchmarks/results/`](./benchmarks/results/)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARIA PROTOCOL v0.5.5                           │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: SERVICE                                               │
│  ├── OpenAI-compatible API (aiohttp, streaming)                 │
│  ├── Desktop App (Tauri 2.0 / Electron, React 18)               │
│  ├── Real-time Web Dashboard (WebSocket)                        │
│  └── Command-Line Interface                                     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: CONSENSUS & MEMORY                                    │
│  ├── Provenance Ledger (blockchain)                             │
│  ├── Proof of Useful Work (every computation is useful)          │
│  ├── Proof of Sobriety (energy tracking)                        │
│  ├── Consent Contracts                                          │
│  └── Prospective Memory (Intention nodes, dual-pathway triggers)│
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: COMPUTE                                               │
│  ├── P2P Network (WebSocket + Kademlia DHT planned v0.6.0)      │
│  ├── Inference Engine (subprocess/native/simulation backends)    │
│  ├── Model Manager (HuggingFace auto-download)                  │
│  ├── Model Sharding & Pipeline Parallelism                      │
│  └── Consent-based Routing                                      │
└─────────────────────────────────────────────────────────────────┘
```

See [Architecture Documentation](docs/architecture.md) for detailed diagrams and explanations.

---

## Desktop App

ARIA Desktop provides a graphical interface for non-developers to run and manage ARIA nodes.

**[Download Latest Release](https://github.com/spmfrance-cloud/aria-protocol/releases/latest)** — Windows, macOS (Intel + Apple Silicon), Linux

Built with **Tauri 2.0** (primary, ~15 MB) and **Electron** (alternative, ~150 MB).

Features:

* One-click node setup and management
* Local AI chat with BitNet models
* Energy consumption tracking and savings dashboard
* Model download and management from HuggingFace
* 12-language interface support (EN, FR, ES, DE, PT, IT, JA, KO, ZH, RU, AR, HI)
* Premium dark mode design with glassmorphism effects
* System tray integration

See [desktop/README.md](desktop/README.md) for build instructions and development guide.

---

## Why ARIA?

| Problem | ARIA's Solution |
|---------|----------------|
| AI requires expensive GPUs | 1-bit models run efficiently on any CPU |
| Data centers waste energy | Distributed across existing consumer devices |
| Users have no control | Explicit consent for every resource used |
| AI outputs are untraceable | Blockchain provenance ledger |
| Computation should be useful | Every cycle produces real AI output (Proof of Useful Work) |
| Models depend on one provider | 8+ organizations produce independent 1-bit models |
| Context windows are limited by RAM | KV-Cache NVMe paging targets 500K+ tokens on 8GB laptops |
| Single model has blind spots | Consensus Inference: multiple models collaborate for higher quality |
| AI forgets between sessions | 5/5 Cognitive Memory Model including prospective memory — one of the first open-source implementations of deferred intentions for AI agents |

### The Numbers

| Metric | Standard LLM | ARIA (1-bit) | Improvement |
|--------|--------------|--------------|-------------|
| Memory (2B model) | 4.0 GB | 0.4 GB | **10x less** |
| Energy (CPU) | 150 mJ/inference | 28 mJ/inference | **5x less** |
| Hardware | GPU ($10K+) | Any CPU | **Free** |
| Models validated | 1-3 per vendor | 9 across 3 vendors | **Ecosystem** |

---

## Supported Models

ARIA supports 1-bit quantized models compatible with [bitnet.cpp](https://github.com/microsoft/BitNet):

| Model | Params | Source | License | HuggingFace |
|-------|--------|--------|---------|-------------|
| BitNet-b1.58-large | 0.7B | Microsoft Research | MIT | [1bitLLM/bitnet_b1_58-large](https://huggingface.co/1bitLLM/bitnet_b1_58-large) |
| Falcon-E-1B-Instruct | 1.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon-E-1B-Instruct-GGUF](https://huggingface.co/tiiuae/Falcon-E-1B-Instruct-GGUF) |
| Falcon3-1B-Instruct-1.58bit | 1.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon3-1B-Instruct-1.58bit-GGUF](https://huggingface.co/tiiuae/Falcon3-1B-Instruct-1.58bit-GGUF) |
| BitNet-b1.58-2B-4T | 2.4B | Microsoft Research | MIT | [microsoft/BitNet-b1.58-2B-4T](https://huggingface.co/microsoft/BitNet-b1.58-2B-4T) |
| Falcon-E-3B-Instruct | 3.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon-E-3B-Instruct-GGUF](https://huggingface.co/tiiuae/Falcon-E-3B-Instruct-GGUF) |
| Falcon3-3B-Instruct-1.58bit | 3.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon3-3B-Instruct-1.58bit-GGUF](https://huggingface.co/tiiuae/Falcon3-3B-Instruct-1.58bit-GGUF) |
| Falcon3-7B-Instruct-1.58bit | 7.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon3-7B-Instruct-1.58bit-GGUF](https://huggingface.co/tiiuae/Falcon3-7B-Instruct-1.58bit-GGUF) |
| Llama3-8B-1.58 | 8.0B | Microsoft/Community | Llama 3 | [HF1BitLLM/Llama3-8B-1.58-100B-tokens](https://huggingface.co/HF1BitLLM/Llama3-8B-1.58-100B-tokens) |
| Falcon3-10B-Instruct-1.58bit | 10.0B | TII (Abu Dhabi) | Apache 2.0 | [tiiuae/Falcon3-10B-Instruct-1.58bit-GGUF](https://huggingface.co/tiiuae/Falcon3-10B-Instruct-1.58bit-GGUF) |

All models use I2_S quantization (ternary weights: {-1, 0, +1}).

### Future (v0.7.0+)

Any model can be converted to 1-bit format via PT-BitNet/PTQTP post-training ternarization. Demonstrated on LLaMA3.x, Qwen3, Qwen2.5 from 0.6B to 70B with 82.4% mathematical reasoning retention.

### 1-Bit Ecosystem

The 1-bit model ecosystem is diversifying rapidly. At least 8 independent organizations are producing 1-bit models and tools:

| Organization | Contribution | License |
|-------------|-------------|---------|
| Microsoft Research | BitNet b1.58, bitnet.cpp | MIT |
| TII (Abu Dhabi) | Falcon-Edge, Falcon3 1.58-bit, onebitllms toolkit | Apache 2.0 |
| MBZUAI + CMU | FBI-LLM: first fully binarized 7B LLM | Open |
| ETH Zurich + Beihang | BiLLM: PTQ 1-bit (ICML 2024) | Open |
| Harbin Institute | OneBit: extreme quantization (NeurIPS 2024) | Open |
| STBLLM | Structured binary quantization (ICLR 2025) | Open |
| HuggingFace | Native BitNet in transformers + Nanotron | Apache 2.0 |
| PT-BitNet / PTQTP | Post-training ternarization for any model | Open |

### Model Download

```bash
# List available models
aria model list

# Download a model
aria model download BitNet-b1.58-2B-4T

# Models are cached in ~/.aria/models/
```

### Backend Modes

```bash
# Auto-detect best available backend
aria node start --backend auto

# Subprocess mode: direct llama-cli bridge (recommended with compiled bitnet.cpp)
aria node start --backend subprocess

# Native mode: Python ctypes bindings to bitnet.cpp shared library
aria node start --backend native

# Simulation mode: no native library needed (for development/testing)
aria node start --backend simulation
```

The **subprocess backend** (v0.5.2+) bridges directly to `llama-cli` from bitnet.cpp, providing real inference with live metrics and proper lifecycle management. This is the recommended approach when bitnet.cpp is compiled on the system.

### Compiling bitnet.cpp

To use native inference, compile bitnet.cpp as a shared library:

```bash
# Clone bitnet.cpp
git clone https://github.com/microsoft/bitnet.cpp
cd bitnet.cpp

# Build shared library
mkdir build && cd build
cmake .. -DBUILD_SHARED_LIBS=ON
cmake --build . --config Release

# Install (choose one):
# Option 1: Copy to ARIA lib directory
mkdir -p ~/.aria/lib
cp libbitnet.so ~/.aria/lib/     # Linux
cp libbitnet.dylib ~/.aria/lib/  # macOS

# Option 2: System-wide install
sudo cp libbitnet.so /usr/local/lib/
sudo ldconfig
```

ARIA auto-detects the library from `~/.aria/lib/`, `/usr/local/lib/`, or the current build directory. If not found, it seamlessly falls back to simulation mode.

---

## Website

Visit [spmfrance-cloud.github.io/aria-protocol](https://spmfrance-cloud.github.io/aria-protocol/) for benchmarks and documentation.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and quick start guide |
| [Architecture](docs/architecture.md) | System design and component details |
| [API Reference](docs/api-reference.md) | OpenAI-compatible API documentation |
| [Protocol Spec](docs/protocol-spec.md) | WebSocket protocol specification |
| [Threat Model](docs/threat-model.md) | Security analysis and mitigations |
| [Security Architecture](docs/security-architecture.md) | Defense-in-depth security model |
| [Benchmarks](benchmarks/README.md) | Performance methodology and results |
| [Roadmap](docs/ROADMAP.md) | Full roadmap v3.0 (9 versions) |
| [Whitepaper](ARIA_Whitepaper.pdf) | Technical whitepaper |

---

## Project Structure

```
aria-protocol/
├── aria/                  # Python backend
│   ├── __init__.py        # Package exports
│   ├── node.py            # Core ARIA node
│   ├── network.py         # P2P WebSocket networking
│   ├── inference.py       # 1-bit inference engine
│   ├── bitnet_native.py   # Native bitnet.cpp bindings (ctypes)
│   ├── bitnet_subprocess.py # Subprocess backend (llama-cli)
│   ├── model_manager.py   # Model download & cache management
│   ├── ledger.py          # Provenance blockchain
│   ├── proof.py           # PoUW & Proof of Sobriety
│   ├── consent.py         # Consent contracts
│   ├── cli.py             # Command-line interface
│   ├── api.py             # OpenAI-compatible API
│   └── dashboard.py       # Real-time web dashboard
├── desktop/               # Desktop app (Tauri + Electron)
│   ├── src-tauri/         # Tauri/Rust backend
│   ├── electron/          # Electron alternative
│   ├── src/               # React frontend (shared)
│   └── package.json       # Node.js dependencies
├── tests/                 # Test suite
├── examples/              # Demo and integration examples
├── docs/                  # Documentation
│   └── ROADMAP.md         # Full roadmap v3.0
├── CHANGELOG.md           # Version history (Keep a Changelog)
└── pyproject.toml         # Package configuration
```

---

## What's Next

ARIA is evolving from a local inference protocol to a fully distributed network. Key innovations in development:

* **Testnet Alpha (v0.6.0)** — Kademlia DHT, NAT traversal, decentralized bootstrap
* **Consensus Inference (v0.7.0)** — Multi-agent orchestrated debate for frontier-quality answers from small models. Research shows 7B models with orchestration reach 92.85% accuracy (Nature 2025, SLM-MATRIX)
* **KV-Cache NVMe Paging (v0.8.0)** — 500K+ token contexts on 8GB RAM laptops via intelligent SSD offloading
* **ARIA-LM (v0.9.0)** — A community-evolving language model improved via distributed reasoning (SAPO) and LoRA merging, without GPU requirements

See the [full roadmap](https://spmfrance-cloud.github.io/aria-protocol/roadmap.html) for all tasks across 9 versions.

---

## Security & Trust Architecture

In decentralized AI, the fundamental question is: **"How do you trust an untrusted node?"** ARIA Protocol answers this with five independent defense layers, where each layer catches failures the others miss.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARIA DEFENSE-IN-DEPTH                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Layer 5: Privacy & Consent                               │  │
│  │  Consent contracts · Data minimization · Local inference   │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Layer 4: Reputation Security                       │  │  │
│  │  │  Reputation scoring · Penalties · Quality threshold │  │  │
│  │  │  ┌───────────────────────────────────────────────┐  │  │  │
│  │  │  │  Layer 3: Consensus Security                  │  │  │  │
│  │  │  │  Proof of Useful Work · Proof of Sobriety     │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  Layer 2: Protocol Security              │  │  │  │  │
│  │  │  │  │  Message auth · Replay protection        │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐   │  │  │  │  │
│  │  │  │  │  │  Layer 1: Transport Security      │   │  │  │  │  │
│  │  │  │  │  │  TLS 1.3 · Certificate validation │   │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘   │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Provenance Ledger (Immutable Core)            │  │
│  │  Every inference recorded: hash, nodes, energy, timestamp  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### How ARIA prevents cheating

| Attack | How it's detected | Mechanism |
|--------|-------------------|-----------|
| **Fake inference** (return garbage to save compute) | Output hash verification + timing analysis | Proof of Useful Work ([`proof.py`](aria/proof.py)) |
| **Energy fraud** (report less energy to inflate reputation) | Cross-reference with hardware TDP + statistical outliers | Proof of Sobriety ([`proof.py`](aria/proof.py)) |
| **Sybil attack** (create fake nodes to game reputation) | IP + hardware fingerprint + reputation requirements | Reputation system ([`proof.py`](aria/proof.py)) |
| **Result manipulation** (alter inference outputs) | Immutable provenance chain + redundant verification | Provenance Ledger ([`ledger.py`](aria/ledger.py)) |
| **Prompt leakage** (spy on user queries) | Local-first inference + consent contracts | Consent system ([`consent.py`](aria/consent.py)) |

### Trust model

Nodes **DO NOT trust each other** — they verify. Users trust their local node (which they control) and the cryptographic proofs on the ledger. Every inference produces an immutable record containing the I/O hashes, participating nodes, energy consumed, and timestamp. This is not a heavyweight blockchain consensus — it's a lightweight provenance chain optimized for AI inference workloads.

📖 **Full details:** [Threat Model](docs/threat-model.md) · [Security Policy](SECURITY.md) · [Protocol Spec](docs/protocol-spec.md)

---

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/spmfrance-cloud/aria-protocol.git
cd aria-protocol

# Install development dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run tests with coverage
make test-cov
```

### Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Ensure** all tests pass (`make test`)
5. **Commit** with clear messages
6. **Push** to your branch
7. **Open** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add type hints to all functions
- Write docstrings for public APIs
- Keep functions focused and small

### Areas to Contribute

- **KV-Cache NVMe** — Prototype SSD-based context extension
- **Consensus Inference** — Multi-agent orchestration protocols
- **Mobile support** - React Native or native iOS/Android apps
- **Additional models** - Support for more 1-bit architectures
- **Performance** - Optimize networking and inference
- **Documentation** - Improve guides and examples
- **Testing** - Expand test coverage

---

## Research Foundations

ARIA's architecture is grounded in peer-reviewed research:

| Area | Key Finding | Source |
|------|------------|--------|
| 1-bit inference | Ternary weights achieve ~10-15% quality loss vs FP16, sufficient for 95% of use cases | Ma et al., arXiv:2402.17764 (2024) |
| Multi-agent quality | 7B models with orchestrated debate reach 92.85% accuracy | SLM-MATRIX, Nature npj (2025) |
| Orchestration protocol | Confidence-based routing outperforms naive debate (avoids groupthink) | SLM-MUX, arXiv:2510.05077 (2025) |
| KV-Cache on SSD | Sparse attention (0.5% of keys cover 90% of attention weight) enables SSD offloading | SpeCache, ICML 2025 |
| KV-Cache quantization | 2-bit KV-cache with <2% accuracy loss enables 1M tokens on single GPU | KIVI, ICML 2024 |
| Distributed RL | Decentralized experience sharing: +94% reward on consumer hardware | SAPO/RLSwarm, Gensyn (2025) |
| Embedding privacy | Projection-based defense reduces inversion from >95% to <5% | Eguard (2024) |
| P2P latency | Modern hybrid DHT+delegated routing achieves <100ms lookups | IPNI + Kademlia + QUIC |

*1-bit = the MP3 of AI. Lossy compression that's good enough for 95% of use cases.*

---

## Roadmap

| Version | Name | Focus | Status |
|---------|----------------|------------------------------------------|-------------|
| v0.1.0 | Genesis | Whitepaper + reference implementation | ✅ Complete |
| v0.2.0 | Full Stack | P2P networking, CLI, API, Dashboard, BitNet | ✅ Complete |
| v0.2.5 | Hardening | Threat model, Protocol spec, TLS support | ✅ Complete |
| v0.3.0 | Benchmarks | Real-world performance validation | ✅ Complete |
| v0.4.0 | Native BitNet | Direct bitnet.cpp integration in Python | ✅ Complete |
| v0.5.0 | Desktop App | Tauri/Electron GUI for non-developers | ✅ Complete |
| v0.5.1 | Build Fix | Desktop build corrections, CI/CD | ✅ Complete |
| v0.5.2 | Subprocess | llama-cli bridge, real inference pipeline | ✅ Complete |
| v0.5.5 | Housekeeping | CI quality gates, version unification, doc sync, security docs, i18n | ✅ Complete |
| v0.6.0 | Testnet Alpha | Kademlia DHT, NAT traversal, bootstrap nodes | 🔄 Current |
| v0.7.0 | Smart Layer | Consensus Inference, 5/5 Cognitive Memory (incl. Prospective Memory), Knowledge Network | ⬜ Planned |
| v0.8.0 | Extended Context | KV-Cache NVMe paging (500K+ tokens on 8GB) | ⬜ Planned |
| v0.9.0 | ARIA-LM | Community-evolving model (SAPO + LoRA merging) | ⬜ Planned |
| v1.0.0 | Production | Stable production network, reputation system | ⬜ Planned |

### Current Focus: v0.6.0 Testnet Alpha

* Kademlia DHT for decentralized peer discovery
* NAT traversal (STUN/TURN)
* Public bootstrap nodes
* Multi-node simulation (50+ nodes)
* Ed25519 message authentication
* Refactor large Python modules into sub-modules

See [full roadmap](https://spmfrance-cloud.github.io/aria-protocol/roadmap.html) for all tasks across 9 versions.

---

## Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/test_node.py -v
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Citation

```bibtex
@misc{aria2026,
  author = {Anthony MURGO},
  title = {ARIA: Autonomous Responsible Intelligence Architecture},
  year = {2026},
  url = {https://github.com/spmfrance-cloud/aria-protocol}
}
```

---

## Acknowledgments

* [Microsoft BitNet](https://github.com/microsoft/BitNet) — 1-bit LLM research and bitnet.cpp
* [TII Falcon](https://huggingface.co/tiiuae) — Falcon-Edge and Falcon3 1.58-bit models
* [Gensyn](https://www.gensyn.ai/) — SAPO/RLSwarm decentralized training research
* [libp2p](https://libp2p.io/) — P2P networking stack inspiration

---

*"The era of centralized AI infrastructure need not be permanent."*
