# ARIA Protocol

**Autonomous Responsible Intelligence Architecture**

> A peer-to-peer protocol for efficient, ethical, and decentralized AI inference.

## The Idea

What if every laptop, phone, and Raspberry Pi could contribute to a global AI network?

ARIA is an open protocol that combines:
- **1-bit model inference** on standard CPUs (no GPU needed)
- **Peer-to-peer distribution** with explicit user consent
- **Blockchain provenance** for full traceability and verification

The result: AI inference that uses **70-82% less energy** than GPU-based systems, runs on **any device**, and is **fully transparent**.

## Why ARIA?

| Problem | ARIA's Answer |
|---------|---------------|
| AI requires expensive GPUs | 1-bit models run on CPUs |
| Data centers waste energy | Distributed across existing devices |
| Users have no control | Explicit consent for every resource |
| AI outputs are untraceable | Blockchain provenance ledger |
| Mining wastes energy | Mining IS inference (Proof of Useful Work) |

## Quick Start

```bash
git clone https://github.com/[your-repo]/aria-protocol.git
cd aria-protocol
python examples/demo.py
```

No dependencies required. No GPU required. Python 3.10+.

## How It Works

### 1. Consent First
Every node explicitly declares what it's willing to contribute:

```python
from aria import ARIANode, ARIAConsent, TaskType

consent = ARIAConsent(
    cpu_percent=25,               # Max 25% of my CPU
    schedule="08:00-22:00",       # Only during these hours
    task_types=[TaskType.TEXT_GENERATION],
    max_ram_mb=512,               # Max 512MB RAM
)

node = ARIANode(consent=consent)
```

### 2. Load a 1-Bit Model
Models use ternary weights (-1, 0, +1). A 2B parameter model fits in 0.4GB:

```python
node.load_model("aria-2b-1bit", num_layers=24)
node.start()
```

### 3. Process Requests, Earn Tokens
```python
result = node.process_request("What is quantum computing?")
# Inference recorded on provenance ledger
# Proof of Useful Work submitted
# ARIA tokens earned
```

### 4. Verify Everything
```python
stats = node.get_stats()
# Provenance: every inference is traceable
# Sobriety: energy consumption is measurable
# Consent: nothing happens without permission
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              ARIA Protocol                   │
├─────────────────────────────────────────────┤
│                                              │
│  Layer 3: SERVICE                            │
│  ├── OpenAI-compatible API                   │
│  ├── Load balancing & routing                │
│  └── Interoperability bridges                │
│                                              │
│  Layer 2: CONSENSUS                          │
│  ├── Provenance Ledger (blockchain)          │
│  ├── Proof of Useful Work (mining=inference) │
│  ├── Proof of Sobriety (energy tracking)     │
│  └── Smart Contracts (consent, rewards)      │
│                                              │
│  Layer 1: COMPUTE                            │
│  ├── P2P network (Kademlia DHT)             │
│  ├── 1-bit inference engine (CPU-native)     │
│  ├── Model sharding & distribution           │
│  └── Consent-based routing                   │
│                                              │
└─────────────────────────────────────────────┘
```

## Key Innovations

### Proof of Useful Work
Bitcoin wastes energy mining arbitrary hashes. In ARIA, **mining IS inference**. Every computation that earns tokens is actual AI work serving real users.

### Proof of Sobriety
Every node measures and reports its energy consumption. The network provides verifiable proof that it uses less energy than centralized alternatives. Every joule is accounted for.

### Consent Contracts
No resource is used without explicit permission. Each node defines exactly what it contributes: how much CPU, when, for what types of tasks, and at what minimum reward. Consent can be changed at any time.

## Project Structure

```
aria-protocol/
├── aria/
│   ├── __init__.py      # Package entry point
│   ├── node.py          # Core ARIA node
│   ├── network.py       # P2P networking & routing
│   ├── inference.py     # 1-bit inference engine
│   ├── ledger.py        # Provenance blockchain
│   ├── consent.py       # Consent contracts
│   └── proof.py         # PoUW & Proof of Sobriety
├── examples/
│   └── demo.py          # Full protocol demonstration
├── ARIA_Whitepaper.pdf  # Technical whitepaper
├── LICENSE              # MIT License
└── README.md            # This file
```

## The Numbers

Based on Microsoft BitNet research:

| Metric | Standard LLM | ARIA (1-bit) | Improvement |
|--------|-------------|--------------|-------------|
| Memory (2B model) | 4.0 GB | 0.4 GB | **10x less** |
| Energy (x86 CPU) | Baseline | -82% | **5.5x less** |
| Speed (x86 CPU) | Baseline | 6.17x | **6x faster** |
| Hardware required | GPU ($10K+) | Any CPU | **Free** |

## Future Work

This is a starting point. The community is invited to:

- [ ] Integrate with bitnet.cpp for real 1-bit inference
- [ ] Implement actual P2P networking (libp2p / asyncio)
- [ ] Deploy smart contracts on EVM-compatible chain
- [ ] Build desktop application (Electron/Tauri)
- [ ] Build mobile application (React Native)
- [ ] Add real tokenizer (BPE/SentencePiece)
- [ ] Implement cross-node pipeline parallelism
- [ ] Add zero-knowledge proofs for private inference
- [ ] Formal security audit

## Contributing

ARIA is MIT licensed. Fork it. Improve it. Build on it.

If this protocol becomes something, remember where it started.

## License

MIT License. See [LICENSE](LICENSE).

## Citation

```
@misc{aria2026,
  author = {Anthony MURGO},
  title = {ARIA: A Peer-to-Peer Efficient AI Inference Protocol},
  year = {2026},
  url = {https://github.com/[your-repo]/aria-protocol}
}
```

---

*"The era of centralized AI infrastructure need not be permanent."*
