# ARIA Protocol — Publication Posts for Community Launch

> Textes prêts à publier pour annoncer ARIA Protocol sur les principales plateformes.
> Données issues des benchmarks réels (v0.3.0, février 2026).

---

## 1. Reddit r/LocalLLaMA

**Titre:** `89 tokens/s on CPU — We built a P2P protocol for distributed 1-bit LLM inference, and it actually works`

---

Hey r/LocalLLaMA,

I've been working on something for a while now and I think it's ready to share. **ARIA** (Autonomous Responsible Intelligence Architecture) is a peer-to-peer protocol for running 1-bit quantized LLMs on CPU, without any GPU requirement. The idea is simple: what if we could pool ordinary computers into a distributed inference network, the way BitTorrent pools bandwidth?

### Why distributed inference matters

We all love running models locally. But there's a ceiling — large models need expensive GPUs, inference-as-a-service costs stack up fast, and the energy footprint of GPU clusters is staggering. Meanwhile, billions of CPUs sit idle around the world.

ARIA takes a different approach. Instead of fighting for GPU access, we leverage 1-bit quantized models (ternary weights: -1, 0, +1) that run efficiently on CPUs. Then we distribute layers across a P2P network so that multiple nodes collaborate on a single inference pipeline. No central server. No cloud dependency. No GPU required.

### Real benchmark numbers

We ran comprehensive benchmarks on an AMD Ryzen 9 7845HX (12C/24T, DDR5). These are real measurements, not projections:

| Model | Params | Throughput (t/s) | Prompt (t/s) | TTFT | RAM | Energy/token |
|---|---|---|---|---|---|---|
| BitNet-b1.58-large | 0.7B | **89.65** | 91.07 | 88 ms | 400 MB | ~11 mJ |
| BitNet-b1.58-2B-4T | 2.4B | **36.94** | 37.45 | 178 ms | 1,300 MB | ~28 mJ |
| Llama3-8B-1.58 | 8.0B | **15.03** | 15.95 | 338 ms | 4,200 MB | ~66 mJ |

A few things stand out:

- **Scaling is sub-linear**: going from 0.7B to 8B (11.4× more parameters) only costs 6× in throughput. That's better than expected.
- **TTFT under 100ms** for the 0.7B model — that's instant for most use cases.
- **RAM stays tiny**: a 2.4B model fits in 1.3 GB. For comparison, the same model in FP16 would need ~5 GB.
- **Energy consumption is absurdly low**: ~28 mJ/token for the 2.4B model, compared to ~5,625 mJ/token on an RTX 4090 and ~7,000 mJ/token via cloud APIs. That's a **99.5% reduction**.

### Thread scaling — the interesting part

We found that 1-bit inference is **memory-bound, not compute-bound**. Performance peaks at 8 threads and degrades beyond that due to cache contention. Going from 8 to 24 threads actually drops throughput from 36.94 to 31.88 t/s.

This is actually great news for distributed inference: instead of throwing more local cores at the problem, you're better off distributing across multiple machines. Our parallel inference test (3 concurrent streams) showed 40.86 t/s combined throughput, confirming the P2P approach.

### Architecture in 3 layers

```
Layer 3 — SERVICE
  OpenAI-compatible API | Web Dashboard | CLI

Layer 2 — CONSENSUS
  Provenance Ledger | Proof of Useful Work | Consent Contracts

Layer 1 — COMPUTE
  P2P Network (WebSocket) | 1-bit Inference Engine | Model Sharding
```

- **Layer 1 (Compute):** WebSocket-based P2P network with model sharding. A 24-layer model gets split across nodes, each holding ~133 MB for a 2B parameter model.
- **Layer 2 (Consensus):** Blockchain-based provenance ledger. Every inference is recorded immutably. Instead of Proof of Work (wasteful hashing), we use **Proof of Useful Work** — mining *is* inference. We also track energy via **Proof of Sobriety** attestations.
- **Layer 3 (Service):** Drop-in replacement for OpenAI's API. Point your existing code at `localhost:3000` and it just works.

### The economic angle

We computed 3-year TCO for 10M tokens/day:

| Solution | 3-Year Cost |
|---|---|
| GPT-4o API | $164,250 |
| Claude 3.5 API | $164,250 |
| Llama via API | $32,850 |
| RTX 4090 local | $8,533 |
| **ARIA (existing CPU)** | **$76** |

Yes, $76 — because you're only paying for electricity.

### What's next

We're at v0.3.0 (benchmarks validated). The roadmap includes native bitnet.cpp integration (v0.4), a desktop app (v0.5), and a testnet with 50+ community nodes (v0.6).

**Contributions are very welcome.** Whether you want to run a node, optimize the inference engine, work on the consensus layer, or just stress-test the protocol — we need you. The codebase is ~5,800 lines of Python, MIT licensed, with 102 tests passing and comprehensive documentation.

**Links:**
- GitHub: https://github.com/spmfrance-cloud/aria-protocol
- Whitepaper: included in the repo (`ARIA_Whitepaper.pdf`)
- Benchmark report: `docs/benchmark-report.md`

Happy to answer any questions. What model sizes would you want to see supported first on the network?

---

## 2. Hacker News

**Titre:** `Show HN: ARIA – P2P distributed inference protocol for 1-bit LLMs on CPU`

---

ARIA is a peer-to-peer protocol for running 1-bit quantized LLMs (ternary weights: -1, 0, +1) on ordinary CPUs. No GPU needed.

We benchmarked on a Ryzen 9: 89.65 t/s for 0.7B params, 36.94 t/s for 2.4B, 15.03 t/s for 8B — all on CPU, at ~28 mJ/token (99.5% less energy than GPU inference).

Key design choices: WebSocket-based P2P with pipeline parallelism for model sharding across nodes. Provenance ledger records every inference immutably. Proof of Useful Work replaces wasteful hash mining — the "mining" is the inference itself. Consent contracts ensure no resource is used without explicit permission.

Drop-in OpenAI-compatible API. ~5,800 lines Python, MIT licensed, 102 tests passing.

https://github.com/spmfrance-cloud/aria-protocol

---

## 3. Twitter/X Thread

---

**Tweet 1/10**

89 tokens/second. On CPU. No GPU.

We just open-sourced ARIA Protocol — a peer-to-peer network for distributed LLM inference using 1-bit quantized models.

Here's what we found 🧵

---

**Tweet 2/10**

The problem: running LLMs requires expensive GPUs, cloud APIs drain your budget, and the energy cost is enormous.

Meanwhile, billions of CPUs sit idle worldwide.

What if we could turn them into a distributed inference network?

---

**Tweet 3/10**

ARIA uses 1-bit quantized models — weights are just -1, 0, or +1. No floating point math needed.

Result: a 2.4B parameter model fits in 1.3 GB of RAM and runs at 36.94 tokens/s on a standard CPU.

---

**Tweet 4/10**

The architecture has 3 layers:

Layer 1: P2P compute network with model sharding
Layer 2: Consensus with Proof of Useful Work (mining = inference)
Layer 3: OpenAI-compatible API — drop-in replacement, zero code changes

---

**Tweet 5/10**

Energy efficiency is where things get wild:

• ARIA (2.4B): ~28 mJ/token
• RTX 4090: ~5,625 mJ/token
• Cloud API: ~7,000 mJ/token

That's a 99.5% reduction. Not a typo.

---

**Tweet 6/10**

We discovered that 1-bit inference is memory-bound, not compute-bound.

Performance peaks at 8 threads. Adding more cores actually hurts — cache contention kills throughput.

This validates the distributed approach: scale out across machines, not up within one.

---

**Tweet 7/10**

Every inference is recorded on an immutable provenance ledger.

No Proof of Work nonsense — we use Proof of Useful Work. The "mining" IS the inference. Every computation produces real value.

Plus: Consent Contracts ensure no resource is used without permission.

---

**Tweet 8/10**

3-year cost comparison for 10M tokens/day:

• GPT-4o: $164,250
• RTX 4090 local: $8,533
• ARIA (existing CPU): $76

Seventy-six dollars. Because you only pay for electricity.

---

**Tweet 9/10**

Full benchmark results:

0.7B → 89.65 t/s | 400 MB RAM | ~11 mJ/token
2.4B → 36.94 t/s | 1.3 GB RAM | ~28 mJ/token
8.0B → 15.03 t/s | 4.2 GB RAM | ~66 mJ/token

Sub-linear scaling: 11.4× more params = only 6× slower.

---

**Tweet 10/10**

ARIA Protocol is MIT licensed, ~5,800 lines of Python, 102 tests passing.

We're looking for contributors — run a node, optimize the engine, break the protocol, or just give feedback.

GitHub: https://github.com/spmfrance-cloud/aria-protocol

Let's decentralize AI inference. For real this time.

---

## 4. LinkedIn Post

---

**Titre:** ARIA Protocol — Quand l'inférence IA devient distribuée, efficiente et éthique

---

Aujourd'hui, nous rendons public **ARIA Protocol**, un projet open-source français qui repense l'inférence des grands modèles de langage.

**Le constat est simple :** l'IA générative repose aujourd'hui sur des GPU coûteux et énergivores, concentrés dans quelques datacenters. Cette centralisation pose des problèmes économiques, environnementaux et de souveraineté technologique.

**Notre approche :** utiliser la quantification 1-bit (poids ternaires : -1, 0, +1) pour exécuter des LLMs directement sur CPU, puis distribuer l'inférence à travers un réseau pair-à-pair.

Les résultats de nos benchmarks parlent d'eux-mêmes :

- **89,65 tokens/s** pour un modèle 0.7B sur CPU standard
- **36,94 tokens/s** pour 2.4B de paramètres, avec seulement 1,3 Go de RAM
- **~28 mJ par token** — soit une réduction de 99,5 % par rapport à l'inférence GPU

L'impact environnemental est considérable. Pour un usage de 10M tokens/jour, ARIA consomme environ 102 kWh/an contre plus de 20 000 kWh/an pour une solution GPU classique. À l'heure où l'empreinte carbone de l'IA est au cœur des préoccupations, ce type d'architecture offre une voie concrète vers une IA plus sobre.

Le protocole intègre un système de **Proof of Useful Work** (le minage produit de l'inférence utile, pas du calcul gaspillé), un **ledger de provenance** immutable pour la traçabilité, et des **contrats de consentement** qui garantissent qu'aucune ressource n'est utilisée sans autorisation explicite.

ARIA est compatible avec l'API OpenAI — aucune modification de code nécessaire pour migrer.

Le projet est en version 0.3.0, sous licence MIT, avec une documentation complète et 102 tests unitaires. Nous cherchons activement des contributeurs, des partenaires académiques et des organisations intéressées par l'inférence distribuée et l'IA responsable.

**GitHub :** https://github.com/spmfrance-cloud/aria-protocol

Si vous travaillez sur l'efficience énergétique de l'IA, l'edge computing, ou les systèmes distribués — discutons-en.

#OpenSource #AI #DistributedSystems #GreenAI #LLM #Innovation #FrenchTech
