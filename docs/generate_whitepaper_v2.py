#!/usr/bin/env python3
"""
ARIA Protocol - Whitepaper v2 Generator
Generates ARIA_Whitepaper_v2.pdf with updated content post-detokenization.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Output directory (relative to this script)
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
chart_dir = os.path.join(output_dir, "charts")
os.makedirs(chart_dir, exist_ok=True)

# ============================
# Color scheme
# ============================
PRIMARY = '#2E86AB'
SECONDARY = '#4ECDC4'
ACCENT = '#A23B72'
DARK = '#1a1a2e'
TEXT = '#333333'
LIGHT_BG = '#e8f4f8'

# ============================
# Charts
# ============================

def create_multiarch_throughput_chart(filename):
    """Create grouped bar chart comparing AMD and Intel throughput."""
    fig, ax = plt.subplots(figsize=(10, 5))
    models = ['0.7B', '2.4B', '8.0B']
    amd = [120.25, 36.62, 15.03]
    intel = [61.81, 77.21, 10.36]
    x = np.arange(len(models))
    w = 0.35
    b1 = ax.bar(x - w/2, amd, w, label='AMD Ryzen 9 7845HX (12C/24T)', color=SECONDARY, edgecolor='white')
    b2 = ax.bar(x + w/2, intel, w, label='Intel i7-11370H (4C/8T)', color=PRIMARY, edgecolor='white')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylabel('Tokens/second', fontsize=11)
    ax.set_title('Multi-Architecture Throughput Comparison', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=8)
    for bar, val in zip(b1, amd):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
               f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold', color=SECONDARY)
    for bar, val in zip(b2, intel):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
               f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold', color=PRIMARY)
    ax.annotate('Intel wins\n(+111%)', xy=(1 + w/2, 77.21), xytext=(1.8, 90),
               arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=2),
               fontsize=9, color='#FF6B6B', fontweight='bold', ha='center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_architecture_chart(filename):
    """Create 5-layer architecture diagram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    layers = ['Layer 5: Intelligence\n(Planned)', 'Layer 4: Reputation', 'Layer 3: Service',
              'Layer 2: Consensus', 'Layer 1: Compute']
    y_pos = range(len(layers))
    layer_colors = ['#FFD93D', ACCENT, PRIMARY, SECONDARY, '#45B7AA']
    bars = ax.barh(y_pos, [1]*5, color=layer_colors, height=0.7, edgecolor='white', linewidth=2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(layers, fontsize=10, fontweight='bold')
    ax.set_xlim(0, 1.2)
    ax.set_xticks([])
    descriptions = [
        'Consensus Inference, Smart Router, ARIA-LM',
        'Contribution scoring, reputation tracking, anti-Sybil',
        'OpenAI-compatible API, CLI, Desktop application',
        'PoUW, Provenance Ledger, Proof of Sobriety',
        'Model sharding, inference pipeline, consent contracts'
    ]
    for i, desc in enumerate(descriptions):
        ax.text(0.5, i, desc, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    ax.set_title('ARIA Protocol — 5-Layer Architecture', fontsize=13, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_competitor_chart(filename):
    """Create competitor positioning chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    projects = ['ARIA\nProtocol', 'Bittensor\nv2', 'Gensyn', 'Render\nNetwork', 'Petals']
    features = [9, 4, 3, 2, 3]  # Features count: consent, privacy, CPU, 1-bit, P2P, energy, provenance, security, desktop
    bar_colors = [SECONDARY, '#FF6B6B', '#FFD93D', '#FFA07A', '#B0B0B0']
    bars = ax.bar(projects, features, color=bar_colors, width=0.6, edgecolor='white', linewidth=2)
    ax.set_ylabel('Differentiating Features', fontsize=11)
    ax.set_title('Feature Comparison vs Competitors', fontsize=13, fontweight='bold', pad=15)
    for bar, val in zip(bars, features):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
               str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 11)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

# ============================
# PDF Generation
# ============================

def create_whitepaper():
    print("Generating Whitepaper v2 charts...")
    create_multiarch_throughput_chart(os.path.join(chart_dir, 'wp2_throughput.png'))
    create_architecture_chart(os.path.join(chart_dir, 'wp2_architecture.png'))
    create_competitor_chart(os.path.join(chart_dir, 'wp2_competitors.png'))

    print("Building Whitepaper v2 PDF...")
    pdf_path = os.path.join(output_dir, "ARIA_Whitepaper_v2.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='WPTitle', parent=styles['Title'], fontSize=26,
        textColor=colors.HexColor(DARK), spaceAfter=8, alignment=TA_CENTER, leading=32))
    styles.add(ParagraphStyle(name='WPSubtitle', parent=styles['Normal'], fontSize=12,
        textColor=colors.HexColor('#666666'), spaceAfter=6, alignment=TA_CENTER, leading=16))
    styles.add(ParagraphStyle(name='WPSection', parent=styles['Heading1'], fontSize=16,
        textColor=colors.HexColor(PRIMARY), spaceBefore=20, spaceAfter=12, leading=20))
    styles.add(ParagraphStyle(name='WPSubsection', parent=styles['Heading2'], fontSize=13,
        textColor=colors.HexColor(ACCENT), spaceBefore=14, spaceAfter=8, leading=16))
    styles.add(ParagraphStyle(name='WPBody', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor(TEXT), spaceAfter=8, alignment=TA_JUSTIFY, leading=14))
    styles.add(ParagraphStyle(name='WPBodyBold', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor(DARK), spaceAfter=8, alignment=TA_JUSTIFY, leading=14,
        fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='WPHighlight', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor(DARK), backColor=colors.HexColor(LIGHT_BG),
        borderPadding=8, spaceAfter=12, spaceBefore=8, leading=14))
    styles.add(ParagraphStyle(name='WPFormula', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor(DARK), alignment=TA_CENTER, spaceAfter=10,
        spaceBefore=8, fontName='Courier', leading=14))
    styles.add(ParagraphStyle(name='WPCaption', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#888888'), alignment=TA_CENTER, spaceAfter=10))

    def make_table(data, col_widths=None, header_color=PRIMARY):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    story = []

    # ========================
    # COVER PAGE
    # ========================
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph("ARIA", styles['WPTitle']))
    story.append(Paragraph("A Peer-to-Peer Efficient AI Inference Protocol", styles['WPSubtitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<i>Autonomous Responsible Intelligence Architecture</i>", styles['WPSubtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Version 2.0", styles['WPSubtitle']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Anthony MURGO", styles['WPSubtitle']))
    story.append(Paragraph("anthony.murgo@outlook.com", styles['WPSubtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("February 2026", styles['WPSubtitle']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("github.com/spmfrance-cloud/aria-protocol", styles['WPSubtitle']))
    story.append(PageBreak())

    # ========================
    # ABSTRACT
    # ========================
    story.append(Paragraph("Abstract", styles['WPSection']))
    story.append(Paragraph(
        "ARIA (Autonomous Responsible Intelligence Architecture) is an open protocol for distributed "
        "AI inference on consumer CPUs. By combining 1-bit quantized large language models (LLMs) with "
        "a peer-to-peer network governed by explicit consent contracts, ARIA enables low-cost, "
        "energy-efficient, and privacy-preserving AI inference without specialized hardware.",
        styles['WPBody']))
    story.append(Paragraph(
        "The protocol introduces a reputation-based contribution system where nodes earn quality scores "
        "through useful work, replacing traditional token-based incentives. A provenance ledger provides "
        "cryptographic verification of all inference operations. Multi-architecture validation across "
        "AMD and Intel CPUs confirms that ARIA achieves 36-120 tokens/second on consumer hardware while "
        "consuming approximately 11-66 mJ per token, representing a 99%+ energy reduction compared to "
        "datacenter GPU inference.",
        styles['WPBody']))
    story.append(Paragraph(
        "ARIA aims to democratize AI by turning billions of idle CPUs worldwide into a distributed "
        "intelligence network, where participation is governed by consent, quality is ensured by "
        "reputation, and provenance is guaranteed by cryptography.",
        styles['WPBody']))
    story.append(PageBreak())

    # ========================
    # 1. INTRODUCTION
    # ========================
    story.append(Paragraph("1. Introduction", styles['WPSection']))
    story.append(Paragraph(
        "Artificial intelligence has become the defining technology of this decade. Large language models "
        "(LLMs) demonstrate remarkable capabilities across text generation, reasoning, code synthesis, "
        "and multimodal understanding. Yet this power is concentrated: a small number of companies "
        "control AI infrastructure through expensive GPU clusters, creating dependency, surveillance "
        "risk, and exclusion for billions of users.",
        styles['WPBody']))
    story.append(Paragraph(
        "Meanwhile, there are an estimated 2-3 billion personal computers worldwide, the vast majority "
        "sitting idle for 90%+ of their operational time. These consumer CPUs represent an enormous "
        "untapped computational resource. The breakthrough of 1-bit quantization (ternary weights: "
        "{-1, 0, +1}) makes it possible for the first time to run meaningful LLMs on standard "
        "CPUs with no GPU requirement.",
        styles['WPBody']))
    story.append(Paragraph(
        "ARIA Protocol combines three key innovations:", styles['WPBodyBold']))
    story.append(Paragraph(
        "<b>1.</b> CPU-native 1-bit inference using ternary lookup tables, eliminating floating-point "
        "multiplication entirely.<br/>"
        "<b>2.</b> Peer-to-peer networking with explicit consent contracts, where every node declares "
        "exactly what it is willing to contribute.<br/>"
        "<b>3.</b> Provenance tracking and reputation scoring, providing cryptographic verification "
        "of all inference operations and quality-based routing.",
        styles['WPBody']))
    story.append(Paragraph(
        "Multi-architecture validation (v0.5.5) demonstrates that this approach is hardware-agnostic: "
        "ARIA runs efficiently on both AMD Zen 4 and Intel Tiger Lake architectures, with performance "
        "characteristics that differ by ISA implementation rather than raw core count.",
        styles['WPBody']))
    story.append(PageBreak())

    # ========================
    # 2. THE PROBLEM
    # ========================
    story.append(Paragraph("2. The Problem", styles['WPSection']))
    story.append(Paragraph(
        "Current AI inference infrastructure suffers from three fundamental problems: centralization, "
        "cost, and opacity.", styles['WPBody']))

    story.append(Paragraph("2.1 Centralization", styles['WPSubsection']))
    story.append(Paragraph(
        "Over 95% of AI inference runs through a handful of providers (OpenAI, Google, Anthropic, Meta). "
        "Users send sensitive prompts to remote servers with no control over data handling, model "
        "behavior, or availability. Service outages, policy changes, or censorship decisions affect "
        "millions of users simultaneously.",
        styles['WPBody']))

    story.append(Paragraph("2.2 Cost", styles['WPSubsection']))
    story.append(Paragraph(
        "GPU-based inference is expensive. A single NVIDIA H100 costs ~$30,000 and consumes 700W. "
        "Cloud API pricing ranges from $0.90 to $60 per million tokens. For organizations processing "
        "millions of tokens daily, this represents a significant operational cost.",
        styles['WPBody']))

    story.append(Paragraph("2.3 Existing Approaches", styles['WPSubsection']))
    comp_data = [
        ['Project', 'Hardware', 'Incentive', 'Consent', 'Privacy', 'Energy Tracking'],
        ['ARIA', 'CPU (1-bit)', 'Reputation', 'Granular', 'Local-first', 'Per-inference'],
        ['Bittensor v2', 'GPU', 'TAO tokens', 'None', 'Cloud', 'None'],
        ['Gensyn', 'GPU', 'Tokens', 'None', 'Cloud', 'None'],
        ['Render', 'GPU', 'RNDR tokens', 'None', 'Cloud', 'None'],
        ['Petals', 'GPU/CPU', 'None', 'None', 'Partial', 'None'],
    ]
    story.append(make_table(comp_data, col_widths=[2.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm]))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "ARIA is unique in combining CPU-first execution, consent-based governance, and per-inference "
        "energy tracking. The Falcon-Edge ecosystem (TII, 2024) validates the 1-bit approach for "
        "edge deployment, while ARIA extends it to a distributed P2P network.",
        styles['WPBody']))
    story.append(PageBreak())

    # ========================
    # 3. PROTOCOL ARCHITECTURE (5 LAYERS)
    # ========================
    story.append(Paragraph("3. Protocol Architecture", styles['WPSection']))
    story.append(Paragraph(
        "ARIA is organized into five distinct layers, each responsible for a specific aspect of "
        "the distributed inference pipeline.",
        styles['WPBody']))
    story.append(Image(os.path.join(chart_dir, 'wp2_architecture.png'), width=14*cm, height=8.4*cm))
    story.append(Paragraph("Figure 1: ARIA 5-layer architecture", styles['WPCaption']))

    story.append(Paragraph("3.1 Layer 1 - Compute", styles['WPSubsection']))
    story.append(Paragraph(
        "The compute layer handles model sharding, inference execution, and consent enforcement. "
        "Models are split into shards distributed across nodes. Each node declares its capabilities "
        "through a consent contract specifying CPU allocation, RAM limits, schedule availability, "
        "accepted task types, and contribution score thresholds.",
        styles['WPBody']))
    story.append(Paragraph(
        "Consent contracts are the ethical backbone of the protocol. No work is assigned to a node "
        "unless it explicitly matches the node's declared consent parameters. This ensures that "
        "every participant has full control over their contribution.",
        styles['WPBody']))

    story.append(Paragraph("3.2 Layer 2 - Consensus", styles['WPSubsection']))
    story.append(Paragraph(
        "<b>Proof of Useful Work (PoUW)</b>: Every inference generates a cryptographic proof binding "
        "the input hash, output hash, computation time, energy consumed, and node identity. Unlike "
        "blockchain proof-of-work, the computation is the useful inference itself, not a waste puzzle.",
        styles['WPBody']))
    story.append(Paragraph(
        "<b>Provenance Ledger</b>: An append-only chain of blocks records all inference operations. "
        "Each record contains the inference hash, node ID, model ID, timestamp, and proof. Users can "
        "independently verify that their query was processed correctly.",
        styles['WPBody']))
    story.append(Paragraph(
        "<b>Proof of Sobriety</b>: Nodes report energy consumption per inference. The protocol "
        "tracks energy efficiency ratings (A+ through F) and provides network-wide savings estimates "
        "compared to datacenter baselines.",
        styles['WPBody']))

    story.append(Paragraph("3.3 Layer 3 - Service", styles['WPSubsection']))
    story.append(Paragraph(
        "ARIA exposes an OpenAI-compatible REST API, enabling zero-code integration with existing "
        "applications. A command-line interface provides developer tools for node management, "
        "benchmarking, and network monitoring. ARIA Desktop, built with Tauri 2.0 and React, "
        "provides a consumer-friendly GUI with 12-language support, allowing non-developers to "
        "contribute to the network in under 60 seconds.",
        styles['WPBody']))

    story.append(Paragraph("3.4 Layer 4 - Reputation", styles['WPSubsection']))
    story.append(Paragraph(
        "The reputation layer replaces traditional token-based incentives with a quality-focused "
        "contribution scoring system. Nodes earn contribution scores based on useful work:",
        styles['WPBody']))
    story.append(Paragraph(
        "Score(n) = base_rate x inferences_completed x quality_score x efficiency_bonus",
        styles['WPFormula']))
    story.append(Paragraph(
        "Where quality_score = f(uptime, latency, verification_pass_rate) in [0, 1] and "
        "efficiency_bonus = g(energy_per_inference / network_average) in [0.5, 2.0]. "
        "Nodes that consume less energy per inference earn up to 2x bonus, directly incentivizing "
        "energy efficiency.",
        styles['WPBody']))
    story.append(Paragraph(
        "Contribution scores are NOT transferable, NOT tradeable, and have NO monetary value. "
        "They serve exclusively as a quality metric for network routing and task assignment. "
        "This eliminates regulatory complexity and aligns incentives purely with network health.",
        styles['WPHighlight']))
    story.append(PageBreak())

    story.append(Paragraph("3.5 Layer 5 - Intelligence (Planned)", styles['WPSubsection']))
    story.append(Paragraph(
        "<b>Consensus Inference</b>: A multi-agent debate protocol where multiple nodes independently "
        "process the same query, then reach consensus through structured argumentation. Research from "
        "Nature (2025) and the SLM-MATRIX framework validates this approach, achieving 92.85% accuracy "
        "with 7B models through multi-agent debate.",
        styles['WPBody']))
    story.append(Paragraph(
        "<b>Smart Router</b>: Confidence-based routing (inspired by SLM-MUX) that directs queries to "
        "the most appropriate model/node combination based on task complexity, required quality, and "
        "node capabilities.",
        styles['WPBody']))
    story.append(Paragraph(
        "<b>ARIA-LM</b>: A community-fine-tuned model evolved through LoRA adapters and SAPO "
        "(Self-play Alignment with Principle Optimization), allowing the network to continuously "
        "improve its own model through decentralized training.",
        styles['WPBody']))
    story.append(Paragraph(
        "<b>Knowledge Network</b>: Distributed retrieval-augmented generation (RAG) via Kademlia DHT, "
        "enabling nodes to share and query a collective knowledge base.",
        styles['WPBody']))

    # ========================
    # 4. CPU-NATIVE 1-BIT INFERENCE
    # ========================
    story.append(Paragraph("4. CPU-Native 1-Bit Inference", styles['WPSection']))
    story.append(Paragraph(
        "The fundamental insight enabling ARIA is that 1-bit (ternary) quantization eliminates "
        "floating-point multiplication entirely. In a standard neural network, the most expensive "
        "operation is matrix multiplication: Y = W x X, where W contains billions of floating-point "
        "weights. With ternary weights ({-1, 0, +1}), this becomes pure addition and subtraction, "
        "implementable as lookup tables (LUTs) that execute efficiently on standard CPU instruction sets.",
        styles['WPBody']))
    story.append(Paragraph(
        "Microsoft's BitNet b1.58 architecture demonstrates that 1-bit models achieve competitive "
        "quality with standard FP16 models while requiring 10-20x less memory and dramatically "
        "less energy. ARIA leverages the bitnet.cpp inference engine which compiles optimized kernels "
        "targeting AVX-512, AVX2, and ARM NEON instruction sets.",
        styles['WPBody']))

    story.append(Paragraph("4.1 Performance Results", styles['WPSubsection']))
    story.append(Image(os.path.join(chart_dir, 'wp2_throughput.png'), width=13*cm, height=6.5*cm))
    story.append(Paragraph("Figure 2: Multi-architecture throughput comparison", styles['WPCaption']))

    perf_data = [
        ['Metric', 'AMD Ryzen 9 7845HX', 'Intel Core i7-11370H'],
        ['Architecture', 'Zen 4 (12C/24T)', 'Tiger Lake (4C/8T)'],
        ['0.7B throughput', '120.25 t/s', '61.81 t/s'],
        ['2.4B throughput', '36.62 t/s', '77.21 t/s'],
        ['8.0B throughput', '~15.03 t/s', '10.36 t/s'],
        ['Memory (2B)', '~0.4 GB', '~0.4 GB'],
        ['Energy (2.4B)', '~28 mJ/token', '~28 mJ/token'],
    ]
    story.append(make_table(perf_data, col_widths=[4*cm, 5*cm, 5*cm]))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph(
        "Multi-architecture validation reveals that 1-bit inference performance is ISA-sensitive. "
        "Intel Tiger Lake with native 512-bit AVX-512 execution units outperforms AMD Zen 4 "
        "(double-pumped 2x256-bit) on the 2.4B model by 111%. This validates ARIA's "
        "hardware-agnostic design: the protocol adapts to the strengths of each architecture.",
        styles['WPHighlight']))
    story.append(PageBreak())

    # ========================
    # 5. PEER-TO-PEER NETWORK DESIGN
    # ========================
    story.append(Paragraph("5. Peer-to-Peer Network Design", styles['WPSection']))

    story.append(Paragraph("5.1 Node Lifecycle", styles['WPSubsection']))
    lifecycle_data = [
        ['Phase', 'Actions', 'Outcome'],
        ['Join', 'Generate key pair, download shards,\npublish consent, build initial reputation', 'Node visible on network'],
        ['Contribute', 'Receive tasks, process inference,\nsubmit proofs, earn contribution score', 'Active network participant'],
        ['Grow', 'Accumulate reputation, receive\nhigher-priority routing', 'Trusted high-value node'],
        ['Leave', 'Graceful disconnect, shards\nredistributed, reputation preserved', 'Can return with history'],
    ]
    story.append(make_table(lifecycle_data, col_widths=[2.5*cm, 5.5*cm, 4.5*cm], header_color=ACCENT))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("5.2 Fault Tolerance", styles['WPSubsection']))
    story.append(Paragraph(
        "ARIA handles node failures through shard replication and pipeline fallback. Each model shard "
        "is held by multiple nodes. When a pipeline stage times out (default: 5 seconds), the network "
        "automatically routes to a replica node. Dead peers are detected via heartbeat (30-second "
        "interval) and pruned from the routing table.",
        styles['WPBody']))

    story.append(Paragraph("5.3 Security", styles['WPSubsection']))
    story.append(Paragraph(
        "ARIA implements a defense-in-depth security model with five layers: transport security "
        "(TLS 1.3), protocol security (message authentication, replay protection), consensus security "
        "(PoUW, PoSobriety), reputation security (reputation-based registration with contribution "
        "history, reputation penalties for fraud), and privacy (consent contracts, data minimization). "
        "A comprehensive threat model documents nine attack vectors with current and planned mitigations.",
        styles['WPBody']))

    # ========================
    # 6. PROVENANCE AND VERIFICATION
    # ========================
    story.append(Paragraph("6. Provenance and Verification", styles['WPSection']))

    story.append(Paragraph("6.1 On-Chain Records", styles['WPSubsection']))
    story.append(Paragraph(
        "Every inference operation is recorded in the provenance ledger as an InferenceRecord containing: "
        "node_id, model_id, input_hash (SHA-256), output_hash, tokens_generated, latency_ms, "
        "energy_mj, and a timestamp. Records are grouped into blocks with Merkle-style chaining.",
        styles['WPBody']))

    story.append(Paragraph("6.2 Protocol Contracts", styles['WPSubsection']))
    contracts_data = [
        ['Contract', 'Purpose'],
        ['ConsentRegistry', 'Stores and validates node consent descriptors'],
        ['InferenceMarket', 'Matches inference requests with available nodes'],
        ['ProvenanceLedger', 'Maintains the immutable inference history chain'],
        ['ContributionTracker', 'Calculates and distributes contribution scores\nbased on useful work metrics'],
    ]
    story.append(make_table(contracts_data, col_widths=[4*cm, 9.5*cm], header_color=SECONDARY))
    story.append(PageBreak())

    # ========================
    # 7. REPUTATION AND CONTRIBUTION SYSTEM
    # ========================
    story.append(Paragraph("7. Reputation and Contribution System", styles['WPSection']))
    story.append(Paragraph(
        "ARIA's contribution system is designed to be simple, fair, and non-financial. Nodes earn "
        "contribution points for useful work. The scoring formula balances quantity, quality, "
        "and efficiency:",
        styles['WPBody']))
    story.append(Paragraph(
        "Score(n) = base_rate x inferences_completed x quality_score x efficiency_bonus",
        styles['WPFormula']))
    story.append(Paragraph(
        "Where:<br/>"
        "- quality_score = f(uptime, latency, verification_pass_rate) in [0, 1]<br/>"
        "- efficiency_bonus = g(energy_per_inference / network_average) in [0.5, 2.0]",
        styles['WPBody']))
    story.append(Paragraph(
        "Nodes that consume less energy per inference earn up to 2x bonus, directly incentivizing "
        "energy efficiency and rewarding efficient CPU architectures.",
        styles['WPBody']))
    story.append(Paragraph(
        "Unlike token-based systems, contribution scores are NOT transferable, NOT tradeable, and "
        "have NO monetary value. They serve exclusively as a quality metric for network routing and "
        "task assignment. This eliminates regulatory complexity and aligns incentives purely with "
        "network health.",
        styles['WPHighlight']))

    story.append(Paragraph("Reputation Properties", styles['WPSubsection']))
    rep_data = [
        ['Property', 'Description'],
        ['Slow to build', 'Consistent quality work over time'],
        ['Fast to lose', 'A single fraud incident has lasting consequences'],
        ['Non-transferable', 'Cannot be bought, sold, or delegated'],
        ['Temporal', 'Decays if node is inactive (encourages sustained contribution)'],
    ]
    story.append(make_table(rep_data, col_widths=[3.5*cm, 10*cm]))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph(
        "Anti-Sybil protection: creating a new node means starting with zero reputation. High-value "
        "tasks require minimum reputation thresholds, making Sybil attacks economically impractical "
        "without token deposits. The cost of building reputation through legitimate contribution "
        "creates a natural barrier against identity farming.",
        styles['WPBody']))

    # ========================
    # 8. REFERENCE IMPLEMENTATION
    # ========================
    story.append(Paragraph("8. Reference Implementation", styles['WPSection']))
    story.append(Paragraph(
        "The reference implementation is open-source (MIT License) and comprises approximately "
        "2,800 lines of Python across 11 modules, with 196 tests passing. The codebase is designed "
        "for readability and extensibility.",
        styles['WPBody']))

    modules_data = [
        ['Module', 'Lines', 'Purpose'],
        ['consent.py', '~150', 'Consent contracts and matching'],
        ['network.py', '~1,250', 'P2P WebSocket networking with TLS'],
        ['node.py', '~250', 'High-level node orchestration'],
        ['proof.py', '~350', 'PoUW and Proof of Sobriety'],
        ['ledger.py', '~300', 'Provenance ledger chain'],
        ['inference.py', '~200', 'BitNet inference engine bindings'],
        ['api_server.py', '~150', 'OpenAI-compatible REST API'],
        ['cli.py', '~150', 'Command-line interface'],
    ]
    story.append(make_table(modules_data, col_widths=[3*cm, 2*cm, 8.5*cm]))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("8.1 Desktop Application", styles['WPSubsection']))
    story.append(Paragraph(
        "ARIA Desktop provides a consumer-friendly interface built with Tauri 2.0 and React. "
        "It supports 12 languages and allows one-click node contribution. Design principle: "
        "a non-developer should be able to become a network contributor in under 60 seconds. "
        "The desktop application includes a model manager, system tray integration, real-time "
        "inference statistics, and automatic update support.",
        styles['WPBody']))
    story.append(PageBreak())

    # ========================
    # 9. FUTURE WORK
    # ========================
    story.append(Paragraph("9. Future Work", styles['WPSection']))
    future_data = [
        ['Version', 'Feature', 'Description'],
        ['v0.6.0', 'Testnet Alpha', 'Kademlia DHT, NAT traversal, bootstrap nodes'],
        ['v0.7.0', 'Smart Layer', 'Consensus Inference, Smart Router, reputation system'],
        ['v0.8.0', 'Extended Context', 'KV-Cache NVMe paging (500K+ tokens on 8GB)'],
        ['v0.8.0', 'Mobile Inference', 'iOS/Android companion app (1B-3B models)'],
        ['v0.9.0', 'ARIA-LM', 'Community LoRA fine-tune via SAPO'],
        ['v0.9.0', 'Knowledge Network', 'Distributed RAG via Kademlia DHT'],
        ['v1.0.0', 'Mainnet', 'Production-ready, third-party audited'],
    ]
    story.append(make_table(future_data, col_widths=[2*cm, 3.5*cm, 8*cm], header_color=ACCENT))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Additional research directions:", styles['WPBodyBold']))
    research_items = [
        "Post-training 1-bit quantization (ternarize existing models)",
        "Hardware optimization: RISC-V, NPU, DSP targets",
        "Zero-knowledge proofs for private inference",
        "Mixture-of-Experts + 1-bit: 100B+ parameters in ~1 GB memory",
    ]
    for item in research_items:
        story.append(Paragraph("- " + item, styles['WPBody']))

    # ========================
    # 10. CONCLUSION
    # ========================
    story.append(Paragraph("10. Conclusion", styles['WPSection']))
    story.append(Paragraph(
        "Just as Linux decentralized operating systems and BitTorrent decentralized file sharing, "
        "ARIA proposes to decentralize AI inference itself. The convergence of 1-bit quantization, "
        "peer-to-peer networking, and consent-based governance creates an opportunity to transform "
        "billions of idle CPUs into a global intelligence network.",
        styles['WPBody']))
    story.append(Paragraph(
        "Our benchmarks demonstrate that this is not theoretical: consumer CPUs today achieve "
        "36-120 tokens per second on 1-bit models, with energy consumption 99% lower than "
        "datacenter alternatives. Multi-architecture validation confirms hardware-agnostic operation "
        "across AMD and Intel platforms.",
        styles['WPBody']))
    story.append(Paragraph(
        "ARIA's contribution system, based on reputation rather than financial tokens, eliminates "
        "speculative dynamics and aligns participation incentives with network quality. The protocol's "
        "consent framework ensures that every contributor maintains full agency over their resources.",
        styles['WPBody']))
    story.append(Paragraph(
        "The reference implementation is open-source, fully tested, and includes a desktop application "
        "for non-technical users. ARIA is ready for community contribution and testnet deployment.",
        styles['WPBody']))
    story.append(PageBreak())

    # ========================
    # REFERENCES
    # ========================
    story.append(Paragraph("References", styles['WPSection']))
    refs = [
        "[1] S. Ma et al. \"The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits.\" arXiv:2402.17764, 2024.",
        "[2] S. Ma et al. \"BitNet: Scaling 1-bit Transformers for Large Language Models.\" arXiv:2310.11453, 2023.",
        "[3] Microsoft Research. \"bitnet.cpp: Fast and Lossless Inference of 1.58-bit LLMs on CPUs.\" GitHub, 2024.",
        "[4] Y. Wang et al. \"Mixture-of-Experts Meets 1-Bit Quantization.\" arXiv, 2024.",
        "[5] P. Maymounkov, D. Mazieres. \"Kademlia: A Peer-to-peer Information System Based on the XOR Metric.\" IPTPS, 2002.",
        "[6] S. Nakamoto. \"Bitcoin: A Peer-to-Peer Electronic Cash System.\" 2008.",
        "[7] A. Tang et al. \"SAPO: Self-play Alignment with Principle Optimization.\" arXiv, 2024.",
        "[8] Bittensor. \"Decentralized Machine Intelligence Network.\" bittensor.com, 2024.",
        "[9] Gensyn. \"Decentralized GPU Training Network.\" gensyn.ai, 2024.",
        "[10] Petals. \"Collaborative Inference of Large Language Models.\" petals.dev, 2023.",
        "[11] TII. \"Falcon3 Family of Open Models.\" arXiv, 2024.",
        "[12] SLM-MATRIX. \"Achieving GPT-4 Level Performance with 7B Models.\" Nature npj, 2025.",
        "[13] SLM-MUX. \"Confidence-based Routing for Multi-agent Systems.\" arXiv:2510.05077, 2025.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, ParagraphStyle('Ref', parent=styles['Normal'], fontSize=8,
            textColor=colors.HexColor('#555555'), spaceAfter=4, leading=11)))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "<b>Document Information</b><br/>"
        "Version: 2.0 | Date: February 2026 | Author: Anthony MURGO<br/>"
        "Repository: github.com/spmfrance-cloud/aria-protocol | License: MIT",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
            textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceBefore=30)))

    doc.build(story)
    print(f"Whitepaper v2 generated: {pdf_path}")

    # Copy to root
    root_path = os.path.join(os.path.dirname(output_dir), "ARIA_Whitepaper_v2.pdf")
    shutil.copy2(pdf_path, root_path)
    print(f"Copied to root: {root_path}")

if __name__ == "__main__":
    create_whitepaper()
