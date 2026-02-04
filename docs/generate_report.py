#!/usr/bin/env python3
"""
ARIA Protocol - Professional Benchmark Report Generator
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Create output directory
output_dir = r"C:\Users\antho\Documents\aria-protocol\docs"
os.makedirs(output_dir, exist_ok=True)

def create_bar_chart_image(data, labels, title, ylabel, filename, colors_list=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    if colors_list is None:
        colors_list = ['#4ECDC4', '#45B7AA', '#3CA99D']
    x = np.arange(len(labels))
    bars = ax.bar(x, data, color=colors_list[:len(data)], width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_ylabel(ylabel)
    for bar, val in zip(bars, data):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data)*0.02,
               f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_comparison_chart(filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    providers = ['GPT-4o', 'Claude 3.5', 'GPT-4o-mini', 'Claude Haiku', 'Llama API', 'ARIA 0.7B', 'ARIA 2.4B', 'ARIA 8.0B']
    costs = [15.00, 15.00, 2.40, 1.25, 0.90, 0.003, 0.008, 0.018]
    colors_list = ['#FF6B6B', '#FF6B6B', '#FFA07A', '#FFA07A', '#FFD93D', '#4ECDC4', '#4ECDC4', '#4ECDC4']
    bars = ax.barh(providers, costs, color=colors_list)
    ax.set_xlabel('Cost per 1M Output Tokens ($)', fontsize=11)
    ax.set_title('Inference Cost Comparison', fontsize=14, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.set_xscale('log')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, cost in zip(bars, costs):
        label = f'${cost:.3f}' if cost < 0.1 else f'${cost:.2f}'
        ax.text(cost * 1.5, bar.get_y() + bar.get_height()/2, label, va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_energy_chart(filename):
    fig, ax = plt.subplots(figsize=(10, 5))
    platforms = ['ARIA 0.7B', 'ARIA 2.4B', 'ARIA 8.0B', 'RTX 4090', 'A100', 'Cloud API']
    energy = [11, 28, 66, 5625, 3333, 7000]
    colors_list = ['#4ECDC4', '#4ECDC4', '#4ECDC4', '#FF6B6B', '#FF6B6B', '#FF6B6B']
    bars = ax.bar(platforms, energy, color=colors_list, width=0.6)
    ax.set_ylabel('Energy per Token (mJ)', fontsize=11)
    ax.set_title('Energy Consumption Comparison', fontsize=14, fontweight='bold', pad=15)
    ax.set_yscale('log')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, energy):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.3,
               f'{val:,} mJ', ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_thread_scaling_chart(filename):
    fig, ax = plt.subplots(figsize=(8, 5))
    threads = [4, 8, 12, 24]
    performance = [36.07, 36.94, 36.76, 31.88]
    ax.plot(threads, performance, 'o-', linewidth=2, markersize=10, color='#2E86AB')
    ax.fill_between(threads, performance, alpha=0.3, color='#2E86AB')
    ax.annotate('Optimal\n(8 threads)', xy=(8, 36.94), xytext=(12, 38),
               arrowprops=dict(arrowstyle='->', color='green', lw=2),
               fontsize=10, color='green', fontweight='bold', ha='center')
    ax.set_xlabel('Number of Threads', fontsize=11)
    ax.set_ylabel('Throughput (tokens/s)', fontsize=11)
    ax.set_title('Thread Scaling Performance (2.4B Model)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(threads)
    ax.set_ylim(30, 40)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_positioning_chart(filename):
    fig, ax = plt.subplots(figsize=(9, 7))
    solutions = [
        (1, 15.0, 800, 'GPT-4o', '#FF6B6B'),
        (1, 15.0, 700, 'Claude 3.5', '#FF8C94'),
        (1, 0.9, 500, 'Llama API', '#FFD93D'),
        (7, 0.05, 600, 'Local GPU\n(RTX 4090)', '#FFA07A'),
        (10, 0.003, 400, 'ARIA 0.7B', '#4ECDC4'),
        (10, 0.008, 500, 'ARIA 2.4B', '#45B7AA'),
        (10, 0.018, 600, 'ARIA 8.0B', '#3CA99D'),
    ]
    for privacy, cost, size, label, color in solutions:
        ax.scatter(privacy, cost, s=size, c=color, alpha=0.7, edgecolors='black', linewidths=1)
        offset_y = cost * 0.3 if cost > 1 else 0.1
        ax.annotate(label, xy=(privacy, cost), xytext=(privacy, cost + offset_y),
                   ha='center', fontsize=9, fontweight='bold')
    ax.set_xlabel('Privacy Score (1=Cloud, 10=Local)', fontsize=11)
    ax.set_ylabel('Cost per 1M Tokens ($)', fontsize=11)
    ax.set_title('ARIA Market Positioning', fontsize=14, fontweight='bold', pad=15)
    ax.set_yscale('log')
    ax.set_xlim(0, 11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

def create_pdf_report():
    print("Generating charts...")
    chart_dir = os.path.join(output_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    
    create_bar_chart_image([89.65, 36.94, 15.03], ['0.7B', '2.4B', '8.0B'], 
        'Throughput by Model Size (tokens/s)', 'Tokens/second',
        os.path.join(chart_dir, 'throughput.png'))
    create_comparison_chart(os.path.join(chart_dir, 'cost.png'))
    create_energy_chart(os.path.join(chart_dir, 'energy.png'))
    create_thread_scaling_chart(os.path.join(chart_dir, 'threads.png'))
    create_positioning_chart(os.path.join(chart_dir, 'positioning.png'))
    
    print("Building PDF...")
    pdf_path = os.path.join(output_dir, "ARIA_Benchmark_Report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='MainTitle', parent=styles['Title'], fontSize=28,
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=14,
        textColor=colors.HexColor('#4a4a4a'), spaceAfter=30, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading1'], fontSize=18,
        textColor=colors.HexColor('#2E86AB'), spaceBefore=25, spaceAfter=15))
    styles.add(ParagraphStyle(name='SubsectionHeader', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#A23B72'), spaceBefore=15, spaceAfter=10))
    styles.add(ParagraphStyle(name='CustomBody', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#333333'), spaceAfter=10, alignment=TA_JUSTIFY, leading=14))
    styles.add(ParagraphStyle(name='Highlight', parent=styles['Normal'], fontSize=11,
        textColor=colors.HexColor('#1a1a2e'), backColor=colors.HexColor('#e8f4f8'),
        borderPadding=10, spaceAfter=15, spaceBefore=10))
    
    story = []
    
    # Cover Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("ARIA PROTOCOL", styles['MainTitle']))
    story.append(Paragraph("Benchmark Report v1.0", styles['Subtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Comprehensive Performance Analysis<br/>& Industry Comparison", styles['Subtitle']))
    story.append(Spacer(1, 1*inch))
    
    metrics_data = [['89.65 t/s', '~11 mJ', '99%', '$0.003'],
                    ['Peak Throughput', 'Energy/Token', 'Energy Savings', 'Cost/1M Tokens']]
    metrics_table = Table(metrics_data, colWidths=[3.5*cm]*4)
    metrics_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 18),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2E86AB')),
        ('FONTSIZE', (0,1), (-1,1), 9),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#666666')),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("February 2026", styles['Subtitle']))
    story.append(Paragraph("github.com/spmfrance-cloud/aria-protocol", styles['Subtitle']))
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    story.append(Paragraph(
        "This report presents comprehensive benchmark results for ARIA Protocol, a peer-to-peer "
        "distributed inference system using 1-bit quantized models. All benchmarks were conducted "
        "on consumer hardware (AMD Ryzen 9 7845HX) with fully reproducible methodology.",
        styles['CustomBody']))
    
    summary_data = [
        ['Metric', 'ARIA (Best)', 'ARIA (Balanced)', 'Industry Standard'],
        ['Throughput', '89.65 t/s', '36.94 t/s', '50-100 t/s (GPU)'],
        ['Energy/Token', '~11 mJ', '~28 mJ', '~3,000-7,000 mJ'],
        ['Hardware Cost', '$0 (existing)', '$0 (existing)', '$1,000-$10,000+'],
        ['Latency (TTFT)', '88 ms', '504 ms', '200-800 ms (API)'],
        ['Privacy', '100% local', '100% local', 'Data sent to cloud'],
    ]
    summary_table = Table(summary_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (1,1), (2,-1), colors.HexColor('#e8f8f5')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Key Findings", styles['SubsectionHeader']))
    findings = [
        "<b>1-bit inference is memory-bound</b> - Optimal performance at 8 threads",
        "<b>Horizontal scaling beats vertical scaling</b> - P2P distribution outperforms multi-threading by 3x",
        "<b>Energy efficiency is 100-250x better</b> than datacenter GPU inference",
        "<b>Sub-linear model scaling</b> - 8B model is 11x larger but only 6x slower than 0.7B"
    ]
    for finding in findings:
        story.append(Paragraph("* " + finding, styles['CustomBody']))
    story.append(PageBreak())
    
    # Performance Results
    story.append(Paragraph("Performance Results", styles['SectionHeader']))
    story.append(Paragraph("Model Size Comparison", styles['SubsectionHeader']))
    story.append(Image(os.path.join(chart_dir, 'throughput.png'), width=14*cm, height=7*cm))
    story.append(Spacer(1, 0.2*inch))
    
    perf_data = [
        ['Model', 'Generation (t/s)', 'Prompt (t/s)', 'ms/token', 'Load Time', 'RAM'],
        ['0.7B', '89.65', '91.07', '11.16', '168 ms', '~400 MB'],
        ['2.4B', '36.94', '37.45', '27.07', '658 ms', '~1,300 MB'],
        ['8.0B', '15.03', '15.95', '66.53', '1,031 ms', '~4,200 MB'],
    ]
    perf_table = Table(perf_data, colWidths=[2*cm, 2.8*cm, 2.5*cm, 2*cm, 2*cm, 2*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4ECDC4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#d4edda')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Thread Scaling Analysis", styles['SubsectionHeader']))
    story.append(Image(os.path.join(chart_dir, 'threads.png'), width=12*cm, height=7.5*cm))
    story.append(Paragraph(
        "<b>Key Insight:</b> More threads does not mean better performance. The 1-bit LUT kernels "
        "are memory-bound, not compute-bound. Peak performance is achieved at 8 threads. "
        "At 24 threads, performance drops by 11.6% due to cache contention.",
        styles['Highlight']))
    story.append(PageBreak())
    
    # Industry Comparison
    story.append(Paragraph("Industry Comparison", styles['SectionHeader']))
    story.append(Paragraph("Inference Cost Comparison", styles['SubsectionHeader']))
    story.append(Image(os.path.join(chart_dir, 'cost.png'), width=14*cm, height=8*cm))
    
    cost_data = [
        ['Provider', 'Model', 'Cost/1M Tokens', 'Privacy', 'Latency'],
        ['OpenAI', 'GPT-4o', '$15.00', 'Cloud', '200-500ms'],
        ['Anthropic', 'Claude 3.5 Sonnet', '$15.00', 'Cloud', '200-600ms'],
        ['Together.ai', 'Llama 3.1 70B', '$0.90', 'Cloud', '300-800ms'],
        ['ARIA', '0.7B (local)', '$0.003', 'Local', '88ms'],
        ['ARIA', '2.4B (local)', '$0.008', 'Local', '504ms'],
        ['ARIA', '8.0B (local)', '$0.018', 'Local', '1,031ms'],
    ]
    cost_table = Table(cost_data, colWidths=[2.5*cm, 3.5*cm, 2.5*cm, 2*cm, 2.5*cm])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0,4), (-1,6), colors.HexColor('#e8f8f5')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(cost_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Energy Consumption Comparison", styles['SubsectionHeader']))
    story.append(Image(os.path.join(chart_dir, 'energy.png'), width=14*cm, height=7*cm))
    story.append(Paragraph(
        "<b>Energy Savings:</b> ARIA achieves 99%+ energy reduction compared to datacenter GPU inference. "
        "This is possible because 1-bit models eliminate floating-point multiplication entirely, "
        "using pure lookup tables that are highly efficient on consumer CPUs.",
        styles['Highlight']))
    story.append(PageBreak())
    
    # Economic Analysis
    story.append(Paragraph("Economic Analysis", styles['SectionHeader']))
    story.append(Paragraph("Total Cost of Ownership (3-Year)", styles['SubsectionHeader']))
    story.append(Paragraph("Scenario: 10 million tokens/day inference workload over 3 years.", styles['CustomBody']))
    
    tco_data = [
        ['Solution', 'Hardware', 'API/Electricity', '3-Year Total', 'vs ARIA'],
        ['GPT-4o', '$0', '$164,250', '$164,250', '2,161x'],
        ['Claude 3.5 Sonnet', '$0', '$164,250', '$164,250', '2,161x'],
        ['Llama API', '$0', '$32,850', '$32,850', '432x'],
        ['RTX 4090 (local)', '$2,000', '$6,533', '$8,533', '112x'],
        ['ARIA (existing CPU)', '$0', '$76', '$76', '1x'],
    ]
    tco_table = Table(tco_data, colWidths=[3.5*cm, 2.5*cm, 3*cm, 2.5*cm, 2*cm])
    tco_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#d4edda')),
        ('FONTNAME', (0,5), (-1,5), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tco_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Market Positioning", styles['SubsectionHeader']))
    story.append(Image(os.path.join(chart_dir, 'positioning.png'), width=13*cm, height=10*cm))
    story.append(PageBreak())
    
    # Conclusions
    story.append(Paragraph("Conclusions", styles['SectionHeader']))
    story.append(Paragraph("Key Findings Summary", styles['SubsectionHeader']))
    
    conclusions_data = [
        ['Finding', 'Implication'],
        ['1-bit inference is memory-bound', 'Optimize for cache, not compute'],
        ['Optimal threads = 8', 'Do not over-parallelize'],
        ['Parallel requests do not scale (+11% only)', 'Use P2P distribution instead'],
        ['99%+ energy reduction', 'Massive sustainability impact'],
        ['$0 hardware cost', 'Democratizes AI inference'],
        ['Sub-linear model scaling', 'Larger models viable on CPU'],
    ]
    conclusions_table = Table(conclusions_data, colWidths=[6*cm, 7.5*cm])
    conclusions_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(conclusions_table)
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph(
        "<b>Document Information</b><br/>"
        "Version: 1.0 | Date: February 2026 | Author: ARIA Protocol Team<br/>"
        "Repository: github.com/spmfrance-cloud/aria-protocol | License: MIT",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
            textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceBefore=30)))
    
    doc.build(story)
    print(f"PDF generated: {pdf_path}")

if __name__ == "__main__":
    create_pdf_report()
