from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib import colors
from datetime import datetime
import os

# Output Directory
OUTPUT_DIR = os.path.expanduser("~/my_projects/Personal/documents")

# Create PDF
pdf_filename = os.path.join(OUTPUT_DIR, "Ollama_Resource_Management_Guide.pdf")
doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    alignment=1  # Center alignment
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2e5c8a'),
    spaceAfter=8,
    spaceBefore=12,
    keepWithNext=True
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#3d7ba8'),
    spaceAfter=6,
    spaceBefore=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    spaceAfter=8
)

code_style = ParagraphStyle(
    'CodeBlock',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=0,
    spaceBefore=0
)

# Inline code style for short snippets
inline_code_style = ParagraphStyle(
    'InlineCode',
    parent=styles['BodyText'],
    fontSize=9,
    fontName='Courier',
    textColor=colors.HexColor('#333333'),
    backColor=colors.HexColor('#f0f0f0'),
    spaceAfter=8,
    leftIndent=20
)

# Table cell style for wrapping text
table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12
)

# Table header style
table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12,
    alignment=1,
    textColor=colors.whitesmoke,
    fontName='Helvetica-Bold'
)

def create_code_block(code_text):
    """Helper function to create a styled code block"""
    code_block = Preformatted(code_text, code_style)
    code_table = Table([[code_block]], colWidths=[6*inch])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return code_table

# Title
elements.append(Paragraph("Ollama Resource Management & Automated Model Switching Guide", title_style))
elements.append(Spacer(1, 0.2*inch))

# Overview
elements.append(Paragraph("Overview", heading_style))
overview_text = """This guide explains how to automatically switch Ollama models and execution modes based on GPU availability. When your <b>Jellyfin server is streaming</b> (using GPU), Ollama will automatically switch to a <b>lightweight CPU-only model</b> to ensure optimal performance for both applications without VRAM conflicts."""
elements.append(Paragraph(overview_text, body_style))
elements.append(Spacer(1, 0.15*inch))

# Section 1: Overview of Resource Management
elements.append(Paragraph("1. Overview: Can You Force Resource Prioritization?", heading_style))
answer_text = """<b>Yes, you can automatically switch models and modes based on resource availability.</b> You can force Ollama to switch to a lighter model (e.g., <b>Llama 3.2:3B Q4</b>) and switch to <b>CPU-only mode</b> when your GPU is in use by Jellyfin. This ensures LLM performance remains usable even when the GPU is occupied."""
elements.append(Paragraph(answer_text, body_style))
elements.append(Spacer(1, 0.15*inch))

# Section 2: Implementation Methods
elements.append(Paragraph("2. How to Implement Resource Prioritization", heading_style))

# Method 1
elements.append(Paragraph("Method 1: Use OLLAMA_MAX_LOADED_MODELS=1", subheading_style))
method1_text = """This ensures <b>only one model is loaded at a time</b>, preventing VRAM conflicts and forcing the system to use available resources efficiently."""
elements.append(Paragraph(method1_text, body_style))
elements.append(create_code_block("environment:\n  - OLLAMA_MAX_LOADED_MODELS=1"))
elements.append(Spacer(1, 0.1*inch))

# Method 2
elements.append(Paragraph("Method 2: Use OLLAMA_NUM_THREADS to Limit CPU Usage", subheading_style))
method2_text = """When running on CPU, limit the number of threads to avoid overloading the system and leaving resources for other containers."""
elements.append(Paragraph(method2_text, body_style))
elements.append(create_code_block("environment:\n  - OLLAMA_NUM_THREADS=6  # Use 6 CPU threads"))
elements.append(Spacer(1, 0.1*inch))

# Method 3
elements.append(Paragraph("Method 3: Use OLLAMA_KV_CACHE_TYPE=q4_0 for Lower VRAM Usage", subheading_style))
method3_text = """This reduces memory usage, making it easier to run on CPU. It also helps when switching between GPU and CPU modes."""
elements.append(Paragraph(method3_text, body_style))
elements.append(create_code_block("environment:\n  - OLLAMA_KV_CACHE_TYPE=q4_0"))
elements.append(Spacer(1, 0.1*inch))

# Method 4
elements.append(Paragraph("Method 4: Use OLLAMA_NUM_PARALLEL=1", subheading_style))
method4_text = """This ensures only <b>one inference request</b> is processed at a time, preventing resource contention and ensuring stability."""
elements.append(Paragraph(method4_text, body_style))
elements.append(create_code_block("environment:\n  - OLLAMA_NUM_PARALLEL=1"))
elements.append(Spacer(1, 0.1*inch))

# Section 3: Automated Model Switching
elements.append(Paragraph("3. Automated Model Switching", heading_style))
switching_text = """You can <b>automatically switch models</b> based on GPU usage. Use a script to detect GPU usage and switch models accordingly."""
elements.append(Paragraph(switching_text, body_style))
elements.append(Spacer(1, 0.1*inch))

# Script Example
elements.append(Paragraph("Script Example", subheading_style))
script_code = """#!/bin/bash
# Check if GPU is in use by Jellyfin
GPU_USAGE=$(nvidia-smi --query-gpu=utilization.gpu \\
  --format=csv,nounits,noheader | cut -d' ' -f1)

if [ "$GPU_USAGE" -gt 50 ]; then
  # GPU is busy, switch to CPU-only mode
  echo "GPU busy. Switching to Llama 3.2:3B Q4 (CPU mode)"
  ollama run llama3.2:3b-instruct-q4_K_M --num-gpu 0
else
  # GPU is free, use full model
  echo "GPU free. Using Qwen2.5-Coder:7B Q4 (GPU mode)"
  ollama run qwen2.5-coder:7b-instruct-q4_K_M --num-gpu 1
fi"""
elements.append(create_code_block(script_code))
elements.append(Spacer(1, 0.15*inch))

# Section 4: Docker Compose Configuration
elements.append(Paragraph("4. Docker Compose Configuration", heading_style))
compose_code = """services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    environment:
      - OLLAMA_KV_CACHE_TYPE=q4_0
      - OLLAMA_NUM_PARALLEL=1
      - OLLAMA_MAX_LOADED_MODELS=1
      - OLLAMA_NUM_THREADS=6
    volumes:
      - ./ollama:/root/.ollama
    ports:
      - "11434:11434"
    devices:
      - /dev/nvidia0:/dev/nvidia0
      - /dev/nvidiactl:/dev/nvidiactl
      - /dev/nvidia-uvm:/dev/nvidia-uvm
    restart: unless-stopped
    runtime: nvidia"""
elements.append(create_code_block(compose_code))
elements.append(Spacer(1, 0.15*inch))

# Section 5: Summary of Resource Management
elements.append(Paragraph("5. Summary of Resource Management", heading_style))
summary_data = [
    [Paragraph("Resource", table_header_style), Paragraph("Use Case", table_header_style), Paragraph("Action", table_header_style)],
    [Paragraph("GPU", table_cell_style), Paragraph("Jellyfin active", table_cell_style), Paragraph("Switch to CPU-only mode for LLM", table_cell_style)],
    [Paragraph("GPU", table_cell_style), Paragraph("Jellyfin inactive", table_cell_style), Paragraph("Use GPU mode for LLM", table_cell_style)],
    [Paragraph("VRAM", table_cell_style), Paragraph("4GB", table_cell_style), Paragraph("Only one model can be loaded at a time", table_cell_style)],
    [Paragraph("CPU", table_cell_style), Paragraph("6 cores", table_cell_style), Paragraph("Use 6 threads for CPU-only mode", table_cell_style)]
]
summary_table = Table(summary_data, colWidths=[1.2*inch, 1.8*inch, 3*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e5c8a')),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
    ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
]))
elements.append(summary_table)
elements.append(Spacer(1, 0.15*inch))

# Final Recommendation
elements.append(Paragraph("Final Recommendation", heading_style))
final_text = """<b>Yes, you can force the model to use fewer resources</b> by:<br/>
1. <b>Switching to a smaller model</b> (e.g., Llama 3.2:3B Q4)<br/>
2. <b>Using CPU-only mode</b> when GPU is busy<br/>
3. <b>Limiting parallel requests</b> and <b>thread usage</b><br/>
This ensures <b>LLM performance remains usable</b> even when Jellyfin is active."""
elements.append(Paragraph(final_text, body_style))
elements.append(Spacer(1, 0.15*inch))

# Footer
elements.append(Paragraph("Document Created On: Friday, January 23, 2026", body_style))
elements.append(Paragraph("Author: Leo (AI Assistant)", body_style))

# Build PDF
doc.build(elements)

print(f"PDF generated: {pdf_filename}")