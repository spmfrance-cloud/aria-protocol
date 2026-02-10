# Security Policy

## Reporting a Vulnerability

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability in ARIA Protocol, please report it responsibly:

- **Email:** security@aria-protocol.org
- **Response time:** We aim to acknowledge reports within 48 hours
- **Disclosure:** We follow coordinated disclosure practices

### What to include

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact assessment
4. Suggested fix (if any)

### Safe Harbor

We will not pursue legal action against security researchers who:
- Act in good faith to avoid privacy violations, data destruction, or service disruption
- Provide us reasonable time to address the issue before public disclosure
- Do not exploit the vulnerability beyond what is necessary to demonstrate it

## Security Architecture

ARIA Protocol secures decentralized AI inference through **five defense layers**, each independently catching failures the others miss:

### Layer 1 — Transport Security
- TLS 1.3 for all WebSocket connections
- Certificate validation and perfect forward secrecy
- Replay protection via timestamps and nonces

### Layer 2 — Protocol Security
- Message authentication with node signatures
- Version negotiation preventing downgrade attacks
- Rate limiting on peer announcements

### Layer 3 — Consensus Security
- **Proof of Useful Work (PoUW):** Mining IS inference — no wasted computation. Every reward requires actual AI inference work, verified via output hashing and timing analysis.
- **Proof of Sobriety:** Energy consumption is tracked per inference and cross-referenced with hardware capabilities. Statistical outlier detection flags impossible claims.
- **Provenance Ledger:** Every inference is recorded immutably — timestamp, I/O hashes, participating nodes, energy consumed. Full audit trail.

### Layer 4 — Economic Security *(designed, implementation v0.7.0–v1.0.0)*
- Stake-based node registration (economic cost to create nodes)
- Slashing conditions for detected fraud
- Time-locked rewards preventing hit-and-run attacks
- Reputation system with slow accrual and fast decay

### Layer 5 — Privacy & Consent
- Consent contracts: explicit CPU, RAM, schedule, and task-type limits
- Data minimization: inference runs locally, no prompts sent to cloud
- End-to-end prompt encryption *(planned)*

## Threat Model

A comprehensive threat model covering P2P attacks (Sybil, Eclipse, MITM), inference integrity attacks (result falsification, pipeline poisoning), economic attacks (energy fraud, reward gaming), and privacy attacks (prompt leakage) is documented in [docs/threat-model.md](docs/threat-model.md).

## Known Limitations

ARIA Protocol is pre-mainnet software. The following security features are designed but not yet implemented:
- Stake-based Sybil resistance (planned v0.7.0)
- Slashing for misbehavior (planned v1.0.0)
- Hardware attestation (planned v1.0.0)
- Third-party security audit (planned v1.0.0)
- Bug bounty program (planned v1.0.0)

We believe in transparency about our security posture. See our [roadmap](docs/ROADMAP.md) for implementation timeline.

## Supported Versions

| Version | Supported |
|---------|-----------|
| v0.5.x  | ✅ Current |
| < v0.5  | ❌ No longer supported |
