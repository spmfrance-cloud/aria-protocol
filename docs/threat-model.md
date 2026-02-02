# ARIA Protocol Threat Model

This document describes the security threat model for ARIA Protocol v0.2.5, including known attack vectors, current mitigations, and planned security improvements.

## Table of Contents

1. [Overview](#overview)
2. [Trust Model](#trust-model)
3. [P2P Network Attacks](#p2p-network-attacks)
4. [Inference Integrity Attacks](#inference-integrity-attacks)
5. [Economic Attacks](#economic-attacks)
6. [Privacy Attacks](#privacy-attacks)
7. [Mitigation Summary](#mitigation-summary)
8. [Security Roadmap](#security-roadmap)

---

## Overview

ARIA Protocol is a decentralized AI inference network where untrusted nodes collaborate to process user queries. This architecture introduces unique security challenges that differ from both traditional centralized AI services and typical blockchain networks.

### Security Assumptions

1. **Adversarial Environment**: Any node may be malicious
2. **Rational Actors**: Most attackers are economically motivated
3. **Network Partition**: Temporary network splits may occur
4. **Cryptographic Primitives**: SHA-256 and standard TLS are secure

### Assets to Protect

| Asset | Confidentiality | Integrity | Availability |
|-------|-----------------|-----------|--------------|
| User prompts/queries | HIGH | MEDIUM | LOW |
| Inference results | LOW | HIGH | MEDIUM |
| Model weights | LOW | HIGH | MEDIUM |
| Energy reports | LOW | HIGH | LOW |
| Node reputation | LOW | HIGH | MEDIUM |
| ARIA tokens | N/A | HIGH | HIGH |

---

## Trust Model

### Participants

```
┌─────────────────────────────────────────────────────────────┐
│                     TRUST RELATIONSHIPS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐         ┌─────────┐         ┌─────────┐      │
│   │  User   │◄───────►│  Node   │◄───────►│  Node   │      │
│   │(Client) │  Trust  │ (Local) │  Verify │(Remote) │      │
│   └─────────┘   ?     └─────────┘         └─────────┘      │
│        │                   │                   │            │
│        │                   │                   │            │
│        ▼                   ▼                   ▼            │
│   ┌─────────────────────────────────────────────────┐      │
│   │              Provenance Ledger                   │      │
│   │         (Cryptographic Verification)             │      │
│   └─────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Trust Levels

| Relationship | Trust Level | Verification Method |
|--------------|-------------|---------------------|
| User → Local Node | HIGH | User controls node |
| User → Remote Node | LOW | Ledger verification |
| Node → Node | LOW | Consensus + Reputation |
| Node → Ledger | HIGH | Cryptographic proofs |
| User → Ledger | HIGH | Independent verification |

### Who Trusts Whom?

1. **Users trust their local node** to:
   - Correctly route requests
   - Not leak prompts to unauthorized parties
   - Report accurate results

2. **Nodes trust the ledger** to:
   - Maintain immutable history
   - Fairly distribute rewards
   - Track reputation accurately

3. **Nodes DO NOT trust other nodes** to:
   - Return correct inference results
   - Report accurate energy consumption
   - Be available when claimed

---

## P2P Network Attacks

### 1. Sybil Attack

**Description**: An attacker creates multiple fake node identities to gain disproportionate influence over the network.

**Impact**:
- Overwhelm routing decisions
- Manipulate reputation scores
- Collect majority of rewards unfairly
- Potentially control inference results

**Attack Vector**:
```
Attacker creates nodes: [A1, A2, A3, ..., An]
Each node announces: high reputation, many shards
Legitimate requests → routed to attacker nodes
```

**Current Mitigations**:
- Proof of Useful Work requires actual computation
- Reputation builds slowly over time
- Quality scoring considers multiple factors

**Planned Mitigations** (v0.4.0):
- [ ] Stake-based node registration (economic cost to create nodes)
- [ ] Identity verification via hardware attestation
- [ ] Social graph analysis for detecting clusters
- [ ] Rate limiting on new node announcements

**Risk Level**: HIGH (v0.2.5) → MEDIUM (planned)

---

### 2. Eclipse Attack

**Description**: An attacker isolates a target node by controlling all its peer connections, allowing manipulation of its view of the network.

**Impact**:
- Target node sees only attacker-controlled peers
- Cannot reach legitimate network
- May accept false information about shards/reputation
- Inference results can be manipulated

**Attack Vector**:
```
1. Attacker identifies target node
2. Floods target with connection requests
3. Fills target's peer table with attacker nodes
4. Target isolated from honest network
```

**Current Mitigations**:
- Bootstrap nodes provide initial connections
- Peer discovery from multiple sources
- Dead peer detection removes unresponsive nodes

**Planned Mitigations** (v0.3.0):
- [ ] Diverse peer selection (by IP range, geography)
- [ ] Persistent peer storage across restarts
- [ ] Outbound connection ratio requirements
- [ ] Peer rotation policies

**Risk Level**: MEDIUM

---

### 3. Man-in-the-Middle (MITM) Attack

**Description**: An attacker intercepts communication between nodes to eavesdrop or modify messages.

**Impact**:
- Read user prompts and responses
- Modify inference requests/results
- Inject false peer information
- Steal authentication tokens

**Attack Vector**:
```
User ──► [Attacker] ──► Node
         ▲
         │ Intercept & modify
         │ all traffic
```

**Current Mitigations**:
- Message integrity via JSON structure
- Node ID verification in messages

**Planned Mitigations** (v0.2.5):
- [x] TLS/WSS for all WebSocket connections
- [ ] Message signing with node keys
- [ ] Certificate pinning for known peers
- [ ] End-to-end encryption for prompts

**Risk Level**: HIGH (without TLS) → LOW (with TLS)

---

## Inference Integrity Attacks

### 4. Result Falsification

**Description**: A malicious node returns incorrect inference results to save computation or cause harm.

**Impact**:
- Users receive wrong/harmful outputs
- Reputation system becomes unreliable
- Network loses utility

**Attack Vector**:
```python
# Malicious node implementation
async def handle_inference(request):
    # Skip actual inference
    return {"output": "random garbage", "tokens": 128}
```

**Current Mitigations**:
- Provenance ledger records all inferences
- Proof of Useful Work requires actual computation
- Reputation tracking over time

**Planned Mitigations** (v0.4.0):
- [ ] Redundant inference (query multiple nodes)
- [ ] Result voting/consensus
- [ ] Cryptographic commitment schemes
- [ ] Zero-knowledge proofs of correct execution
- [ ] Slashing for detected falsification

**Detection Methods**:
1. **Spot checking**: Re-run random samples
2. **Consistency**: Compare with known-good results
3. **Timing analysis**: Too-fast responses are suspicious
4. **Output validation**: Statistical analysis of outputs

**Risk Level**: HIGH

---

### 5. Pipeline Poisoning

**Description**: In distributed inference, a malicious node corrupts intermediate activations to affect final output.

**Impact**:
- Subtle corruption of results
- Difficult to detect source
- May persist across many inferences

**Attack Vector**:
```
Layer 0-7    Layer 8-15    Layer 16-23
[Honest] ──► [Malicious] ──► [Honest]
              ▲
              │ Corrupt activations
```

**Current Mitigations**:
- Activation serialization with checksums
- Timeout and fallback to replicas

**Planned Mitigations**:
- [ ] Activation range validation
- [ ] Redundant pipeline paths
- [ ] Checkpoint verification
- [ ] Statistical anomaly detection

**Risk Level**: MEDIUM

---

## Economic Attacks

### 6. Energy Fraud

**Description**: Nodes report false energy consumption to game the Proof of Sobriety system and earn higher rewards.

**Impact**:
- Unfair reward distribution
- Undermines efficiency incentives
- Environmental claims become unreliable

**Attack Vector**:
```python
# Malicious energy reporting
def report_energy(actual_mj):
    # Report 50% less energy than actual
    return actual_mj * 0.5
```

**Current Mitigations**:
- Energy estimation based on computation
- Cross-reference with latency
- Statistical outlier detection

**Planned Mitigations** (v0.4.0):
- [ ] Hardware attestation (TPM/SGX)
- [ ] External power monitoring integration
- [ ] Benchmark-based calibration
- [ ] Slashing for proven fraud

**Detection Methods**:
1. **Latency correlation**: Energy should correlate with time
2. **Hardware profiling**: Known CPU TDP limits
3. **Statistical analysis**: Detect impossible values
4. **Peer comparison**: Similar hardware, similar energy

**Risk Level**: MEDIUM

---

### 7. Reward Gaming

**Description**: Nodes exploit the reward mechanism to earn tokens without providing proportional value.

**Impact**:
- Token inflation
- Honest nodes earn less
- Economic model breaks down

**Attack Vectors**:
- Self-dealing: Send requests to own nodes
- Collusion: Coordinate with other attackers
- Free-riding: Accept work but don't complete it

**Current Mitigations**:
- Proof of Useful Work ties rewards to computation
- Reputation affects reward multiplier
- Request fees create cost for attackers

**Planned Mitigations** (v0.4.0):
- [ ] Request origin verification
- [ ] Fee burning mechanism
- [ ] Time-locked rewards
- [ ] Collusion detection algorithms

**Risk Level**: MEDIUM

---

## Privacy Attacks

### 8. Prompt Leakage

**Description**: Malicious nodes collect and expose user prompts, potentially revealing sensitive information.

**Impact**:
- User privacy violation
- Potential for blackmail/harassment
- Regulatory compliance issues (GDPR, etc.)

**Attack Vector**:
```python
# Malicious node logging
async def handle_inference(request):
    # Log prompt to attacker's server
    await leak_to_server(request["query"])
    return normal_inference(request)
```

**Current Mitigations**:
- Consent contracts specify privacy preferences
- Users can run local nodes
- No central logging by design

**Planned Mitigations** (v0.3.0):
- [ ] Prompt encryption (homomorphic or MPC)
- [ ] Trusted execution environments (TEE)
- [ ] Differential privacy for activations
- [ ] Audit logging with retention policies

**Privacy Levels**:
| Level | Description | Protection |
|-------|-------------|------------|
| 0 | Public | None - prompts may be logged |
| 1 | Standard | TLS in transit, no persistent storage |
| 2 | Private | Encrypted prompts, TEE execution |
| 3 | Maximum | Local-only inference |

**Risk Level**: HIGH

---

### 9. Activation Analysis

**Description**: Intermediate activations in pipeline inference may reveal information about the input.

**Impact**:
- Partial prompt reconstruction
- Inference about user intent
- Model inversion attacks

**Attack Vector**:
```
Activations flowing: [H1] ──► [H2] ──► [H3]
                           ▲
                           │ Analyze patterns
                           │ to infer input
```

**Current Mitigations**:
- Activations not persisted
- Short pipeline timeouts

**Planned Mitigations**:
- [ ] Activation noise injection
- [ ] Secure multi-party computation
- [ ] Activation encryption between stages

**Risk Level**: LOW-MEDIUM

---

## Mitigation Summary

### Current Status (v0.2.5)

| Threat | Severity | Mitigation Status |
|--------|----------|-------------------|
| Sybil Attack | HIGH | PARTIAL |
| Eclipse Attack | MEDIUM | PARTIAL |
| MITM Attack | HIGH | IMPLEMENTED (TLS) |
| Result Falsification | HIGH | PARTIAL |
| Pipeline Poisoning | MEDIUM | PARTIAL |
| Energy Fraud | MEDIUM | PARTIAL |
| Reward Gaming | MEDIUM | PARTIAL |
| Prompt Leakage | HIGH | PARTIAL |
| Activation Analysis | LOW | MINIMAL |

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Transport Security                                │
│  ├── TLS 1.3 for all connections                           │
│  ├── Certificate validation                                 │
│  └── Perfect forward secrecy                                │
│                                                             │
│  Layer 2: Protocol Security                                 │
│  ├── Message authentication                                 │
│  ├── Replay protection (timestamps)                        │
│  └── Version negotiation                                    │
│                                                             │
│  Layer 3: Consensus Security                                │
│  ├── Proof of Useful Work                                   │
│  ├── Proof of Sobriety                                      │
│  └── Reputation system                                      │
│                                                             │
│  Layer 4: Economic Security                                 │
│  ├── Stake requirements (planned)                          │
│  ├── Slashing conditions (planned)                         │
│  └── Fee mechanisms                                         │
│                                                             │
│  Layer 5: Privacy                                           │
│  ├── Consent contracts                                      │
│  ├── Data minimization                                      │
│  └── Encryption (planned)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Roadmap

### v0.2.5 (Current)

- [x] TLS/WSS support for WebSocket connections
- [x] Self-signed certificate generation
- [x] Threat model documentation
- [ ] Basic input validation hardening

### v0.3.0 (Mobile)

- [ ] End-to-end prompt encryption
- [ ] Peer diversity requirements
- [ ] Certificate pinning
- [ ] Mobile-specific security (keychain, etc.)

### v0.4.0 (Consensus)

- [ ] Stake-based Sybil resistance
- [ ] Slashing for misbehavior
- [ ] Hardware attestation integration
- [ ] Redundant inference consensus

### v1.0.0 (Mainnet)

- [ ] Third-party security audit
- [ ] Bug bounty program
- [ ] Formal verification of critical paths
- [ ] Production hardening

---

## Reporting Security Issues

If you discover a security vulnerability in ARIA Protocol:

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: security@aria-protocol.org
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours and will work with you on coordinated disclosure.

---

## References

- [Bitcoin Security Model](https://bitcoin.org/en/bitcoin-paper)
- [Ethereum Threat Model](https://ethereum.org/en/developers/docs/security/)
- [OWASP P2P Security](https://owasp.org/www-project-p2p-security/)
- [Sybil Attack Paper](https://www.microsoft.com/en-us/research/publication/the-sybil-attack/)

---

*Document Version: 0.2.5*
*Last Updated: 2026-02-01*
