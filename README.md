# ARIA Protocol

![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Tests](https://img.shields.io/badge/tests-102%20passing-brightgreen.svg)
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
| **bitnet.cpp Integration** | Real 1-bit inference kernels | ✅ Validated |

---

## Benchmarks

Real-world performance on AMD Ryzen 9 7845HX (8 threads):

| Model | Params | Tokens/s | Energy* |
|-------|--------|----------|---------|
| BitNet-b1.58-large | 0.7B | 89.65 t/s | ~11 mJ/token |
| BitNet-b1.58-2B-4T | 2.4B | 36.94 t/s | ~28 mJ/token |
| Llama3-8B-1.58 | 8.0B | 15.03 t/s | ~66 mJ/token |

*Energy is estimated via CPU-time × TDP. See [benchmarks documentation](./benchmarks/README.md) for methodology and limitations.

Key findings:
- **Thread scaling**: Optimal at 8 threads; 1-bit LUT kernels are memory-bound
- **Parallel inference**: 3 concurrent streams yield only +11% throughput → validates P2P architecture
- **Context length**: Stable performance (-7% degradation from 32 to 1024 tokens)

All benchmarks are reproducible:
```bash
pip install -e .
python benchmarks/run_benchmark.py --prompts 5 --output results.json
```

Full results: [`benchmarks/results/`](./benchmarks/results/)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARIA PROTOCOL v0.2.5                       │
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
│  ├── 1-bit Inference Engine                                     │
│  ├── Model Sharding & Distribution                              │
│  └── Consent-based Routing                                      │
└─────────────────────────────────────────────────────────────────┘
```

See [Architecture Documentation](docs/architecture.md) for detailed diagrams and explanations.

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

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and quick start guide |
| [Architecture](docs/architecture.md) | System design and component details |
| [API Reference](docs/api-reference.md) | OpenAI-compatible API documentation |
| [Protocol Spec](docs/protocol-spec.md) | WebSocket protocol specification |
| [Threat Model](docs/threat-model.md) | Security analysis and mitigations |
| [Benchmarks](benchmarks/README.md) | Performance methodology and results |
| [Whitepaper](ARIA_Whitepaper.pdf) | Technical whitepaper |

---

## Project Structure

```
aria-protocol/
├── aria/
│   ├── __init__.py      # Package exports
│   ├── node.py          # Core ARIA node
│   ├── network.py       # P2P WebSocket networking
│   ├── inference.py     # 1-bit inference engine
│   ├── ledger.py        # Provenance blockchain
│   ├── proof.py         # PoUW & Proof of Sobriety
│   ├── consent.py       # Consent contracts
│   ├── cli.py           # Command-line interface
│   ├── api.py           # OpenAI-compatible API
│   └── dashboard.py     # Real-time web dashboard
├── tests/               # Test suite (102 tests)
├── examples/            # Demo and integration examples
├── docs/                # Documentation
└── pyproject.toml       # Package configuration
```

---

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/aria-protocol/aria-protocol.git
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

## Roadmap

| Version | Name | Focus | Status |
|---------|------|-------|--------|
| v0.1.0 | Genesis | Whitepaper + reference implementation | ✅ Complete |
| v0.2.0 | Full Stack | P2P networking, CLI, API, Dashboard, BitNet | ✅ Complete |
| v0.2.5 | Hardening | Threat model, Protocol spec, TLS support | ✅ Complete |
| v0.3.0 | Benchmarks | Real-world performance validation | ✅ Complete |
| v0.4.0 | Native BitNet | Direct bitnet.cpp integration in Python | 🔄 Next |
| v0.5.0 | Desktop App | Electron/Tauri GUI for non-developers | ⬜ Planned |
| v0.6.0 | Testnet Alpha | Public bootstrap nodes, 50+ community nodes | ⬜ Planned |
| v0.7.0 | Reputation | Node reliability scoring, anti-Sybil | ⬜ Planned |
| v0.8.0 | Mobile | iOS/Android nodes with on-device inference | ⬜ Planned |
| v1.0.0 | Mainnet | Production network, token economics, DAO | ⬜ Planned |

### Current Focus: v0.4.0 Native BitNet

- [ ] Direct Python bindings for bitnet.cpp
- [ ] Auto-download models from HuggingFace
- [ ] Seamless fallback simulation → real inference
- [ ] Integration tests with real 1-bit weights

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
  url = {https://github.com/aria-protocol/aria-protocol}
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
