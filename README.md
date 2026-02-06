# ARIA Protocol

![Version](https://img.shields.io/badge/version-0.5.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Tests](https://img.shields.io/badge/tests-176%20passing-brightgreen.svg)
![Benchmarks](https://img.shields.io/badge/benchmarks-reproducible-blue.svg)

**Autonomous Responsible Intelligence Architecture**

> A peer-to-peer protocol for efficient, ethical, and decentralized AI inference.

## What is ARIA?

ARIA is an open protocol that enables distributed AI inference across consumer devices. By combining **1-bit model inference**, **peer-to-peer networking**, and **blockchain provenance**, ARIA creates a decentralized AI network that is:

- **70-82% more energy efficient** than GPU-based systems
- **Runs on any CPU** (no expensive hardware required)
- **Fully transparent** with immutable inference records
- **Consent-based** - no resource used without permission

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
| **Proof of Useful Work** | Mining = Inference (no wasted computation) | ✅ Complete |
| **Proof of Sobriety** | Verifiable energy efficiency attestations | ✅ Complete |
| **Consent Contracts** | Explicit resource usage permissions | ✅ Complete |
| **bitnet.cpp Integration** | Real 1-bit inference kernels | ✅ Complete |
| **Native BitNet** | Python ctypes bindings to bitnet.cpp | ✅ Complete |
| **Subprocess Backend** | llama-cli process-based inference | ✅ Complete |
| **Model Manager** | Auto-download models from HuggingFace | ✅ Complete |

---

## Benchmarks

### v0.5.2 — Subprocess backend (latest)

Real-world performance on AMD Ryzen 9 7845HX (8 threads, subprocess backend calling llama-cli):

| Model | Params | Avg tok/s | Avg latency | Avg energy* |
|-------|--------|-----------|-------------|-------------|
| BitNet-b1.58-large | 0.7B | **120.25** | 588 ms | 8,823 mJ |
| BitNet-b1.58-2B-4T | 2.4B | **36.62** | 2,120 ms | 31,807 mJ |

### v0.3.0 — Direct bitnet.cpp benchmarks

Earlier benchmarks using bitnet.cpp directly (different methodology, not directly comparable):

| Model | Params | Tokens/s | Energy* |
|-------|--------|----------|---------|
| BitNet-b1.58-large | 0.7B | 89.65 t/s | ~11 mJ/token |
| BitNet-b1.58-2B-4T | 2.4B | 36.94 t/s | ~28 mJ/token |
| Llama3-8B-1.58 | 8.0B | 15.03 t/s | ~66 mJ/token |

*Energy is estimated via CPU-time × TDP/threads — not a direct hardware measurement (no RAPL). See [benchmarks documentation](./benchmarks/README.md) for methodology and limitations.

Key findings:
- **Thread scaling**: Optimal at 8 threads; 1-bit LUT kernels are memory-bound
- **Parallel inference**: 3 concurrent streams yield only +11% throughput → validates P2P architecture
- **Context length**: Stable performance (-7% degradation from 32 to 1024 tokens)

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
│                      ARIA PROTOCOL v0.5.2                       │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: SERVICE                                               │
│  ├── OpenAI-compatible API (aiohttp)                            │
│  ├── Real-time Web Dashboard                                    │
│  └── Command-Line Interface                                     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: CONSENSUS                                             │
│  ├── Provenance Ledger (blockchain)                             │
│  ├── Proof of Useful Work (mining = inference)                  │
│  ├── Proof of Sobriety (energy tracking)                        │
│  └── Consent Contracts                                          │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: COMPUTE                                               │
│  ├── P2P Network (WebSocket)                                    │
│  ├── Native BitNet Engine (ctypes → bitnet.cpp)                 │
│  ├── Subprocess Backend (llama-cli → bitnet.cpp)                │
│  ├── Simulation Backend (protocol testing)                      │
│  ├── Model Manager (HuggingFace auto-download)                  │
│  ├── Model Sharding & Distribution                              │
│  └── Consent-based Routing                                      │
└─────────────────────────────────────────────────────────────────┘
```

See [Architecture Documentation](docs/architecture.md) for detailed diagrams and explanations.

---

## Desktop App

ARIA Desktop provides a graphical interface for non-developers to run and manage ARIA nodes.

| Platform | Architecture | Download |
|----------|-------------|----------|
| Windows 10+ | x64 | [Download .exe](https://github.com/spmfrance-cloud/aria-protocol/releases/latest) |
| macOS 11+ | Intel | [Download .dmg](https://github.com/spmfrance-cloud/aria-protocol/releases/latest) |
| macOS 11+ | Apple Silicon | [Download .dmg](https://github.com/spmfrance-cloud/aria-protocol/releases/latest) |
| Ubuntu 20.04+ | x64 | [Download .AppImage](https://github.com/spmfrance-cloud/aria-protocol/releases/latest) |

Built with **Tauri 2.0** (primary, ~15 MB) and **Electron** (alternative, ~150 MB).

Features:
- One-click node setup and management
- Local AI chat with BitNet models
- Energy consumption tracking and savings dashboard
- Model download and management
- 12-language interface support
- System tray integration

See [desktop/README.md](desktop/README.md) for build instructions and development guide.

---

## Why ARIA?

| Problem | ARIA's Solution |
|---------|-----------------|
| AI requires expensive GPUs | 1-bit models run efficiently on any CPU |
| Data centers waste energy | Distributed across existing consumer devices |
| Users have no control | Explicit consent for every resource used |
| AI outputs are untraceable | Blockchain provenance ledger |
| Crypto mining wastes energy | Mining IS inference (Proof of Useful Work) |

### The Numbers

| Metric | Standard LLM | ARIA (1-bit) | Improvement |
|--------|--------------|--------------|-------------|
| Memory (2B model) | 4.0 GB | 0.4 GB | **10x less** |
| Energy (CPU) | 150 mJ/inference | 28 mJ/inference | **5x less** |
| Hardware | GPU ($10K+) | Any CPU | **Free** |

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
| [Benchmarks](benchmarks/README.md) | Performance methodology and results |
| [Roadmap](docs/ROADMAP.md) | Full roadmap v2.1 (62 tasks, 9 versions) |
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
│   └── ROADMAP.md         # Full roadmap v2.1
├── CHANGELOG.md           # Version history (Keep a Changelog)
└── pyproject.toml         # Package configuration
```

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

- **bitnet.cpp integration** - Connect real 1-bit inference kernels
- **Mobile support** - React Native or native iOS/Android apps
- **Additional models** - Support for more 1-bit architectures
- **Performance** - Optimize networking and inference
- **Documentation** - Improve guides and examples
- **Testing** - Expand test coverage

---

## 🗺️ Roadmap

> **[📋 Full Roadmap v2.1 →](docs/ROADMAP.md)** — 9 versions, 62 tasks, from v0.5.2 to v1.1.0+

| Version | Name | Focus | Status |
|---------|------|-------|--------|
| v0.1→v0.5.2 | Genesis → Desktop | Whitepaper, P2P, CLI, API, BitNet, Benchmarks, Desktop App | ✅ Complete |
| v0.5.5 | Housekeeping | Repo update, desktop↔backend integration, model validation | 🔥 Next |
| v0.6.0 | Testnet Alpha | Bootstrap nodes, Falcon3/Edge models, hardened P2P, 50+ nodes | ⬜ Planned |
| v0.7.0 | Smart Layer | Reputation, Smart Router, frontier API overlay | ⬜ Planned |
| v0.7.5 | R&D + Docs | PT-BitNet, Whitepaper v2, site redesign | ⬜ Planned |
| v0.8.0 | Collective Intelligence | Consensus Inference, RAG, ARIA Code, vision | ⬜ Planned |
| v0.9.0 | ARIA-LM + Ecosystem | Community fine-tune, MCP, browser agent | ⬜ Planned |
| v1.0.0 | Mainnet | $ARIA token, DAO, staking, audit | ⬜ Planned |
| v1.1.0+ | Beyond | Mobile, Computer Use, MoE+1-bit, SDK | 🔮 Vision |

---

## Native BitNet Integration

ARIA supports native Python bindings for bitnet.cpp via ctypes, alongside a subprocess backend using llama-cli.

### Supported Models

| Model | Params | HuggingFace Repo |
|-------|--------|------------------|
| BitNet-b1.58-large | 0.7B | `microsoft/bitnet-b1.58-large` |
| BitNet-b1.58-2B-4T | 2.4B | `microsoft/bitnet-b1.58-2B-4T` |
| Llama3-8B-1.58 | 8.0B | `microsoft/Llama3-8B-1.58-100B-tokens` |

### Model Download

```bash
# List available models
aria model list

# Download a model
aria model download BitNet-b1.58-2B-4T

# Models are cached in ~/.aria/models/
```

### Backend Modes

ARIA supports 3 inference backends:

| Backend | Description | Requirements |
|---------|-------------|--------------|
| `native` | Python ctypes bindings to bitnet.cpp shared library | Compiled `libbitnet.so`/`.dll` |
| `subprocess` | Spawns `llama-cli` from bitnet.cpp as a child process | bitnet.cpp build with `llama-cli` binary |
| `simulation` | Simulated inference for protocol development and testing | None |

```bash
# Auto-detect: use native bitnet.cpp if available, else simulation
aria node start --backend auto

# Force native mode (requires compiled bitnet.cpp shared library)
aria node start --backend native

# Force subprocess mode (requires llama-cli binary from bitnet.cpp)
aria node start --backend subprocess

# Force simulation mode (no native library needed)
aria node start --backend simulation
```

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

- [Microsoft BitNet](https://github.com/microsoft/BitNet) - 1-bit LLM research
- [bitnet.cpp](https://github.com/microsoft/bitnet.cpp) - Efficient 1-bit inference

---

<p align="center">
  <i>"The era of centralized AI infrastructure need not be permanent."</i>
</p>
