from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Preformatted, KeepTogether
from reportlab.lib import colors
from datetime import datetime
import os

# Output Directory
OUTPUT_DIR = os.path.expanduser("~/my_projects/Personal/documents")

# Create PDF
pdf_filename = os.path.join(OUTPUT_DIR, "Ollama_Jellyfin_Setup_Documentation.pdf")
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

# Title
elements.append(Paragraph("Technical Setup Documentation: Ollama + Jellyfin on Intel i5-11400 with NVIDIA T4000", title_style))
elements.append(Spacer(1, 0.2*inch))

# Overview
elements.append(Paragraph("Overview", heading_style))
overview_text = """This document summarizes the technical considerations, performance expectations, and configuration recommendations for running <b>Ollama</b> (for AI inference) and <b>Jellyfin</b> (for media streaming) on a system with the following specifications:<br/>
• <b>CPU</b>: Intel Core i5-11400 (6 cores, 12 threads, 11th Gen)<br/>
• <b>RAM</b>: 64GB DDR4<br/>
• <b>GPU</b>: NVIDIA PNY T4000 (4GB VRAM)<br/>
• <b>Use Case</b>: Dual-purpose system for AI inference (LLMs) and HD media streaming<br/>
• <b>Containerization</b>: Docker-based setup with Ollama and Jellyfin running in containers"""
elements.append(Paragraph(overview_text, body_style))
elements.append(Spacer(1, 0.15*inch))

# Section 1: System Capabilities and Limitations
hardware_data = [
    ["Component", "Specification"],
    ["CPU", "Intel Core i5-11400 (11th Gen, 6C/12T)"],
    ["RAM", "64GB DDR4 (sufficient for containerized workloads)"],
    ["GPU", "NVIDIA PNY T4000 (4GB VRAM, CUDA-capable)"],
    ["Use Case", "Mixed workload: AI inference + HD media streaming"]
]
hardware_table = Table(hardware_data, colWidths=[1.5*inch, 4.5*inch])
hardware_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e5c8a')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 10),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
    ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ('FONTSIZE', (0,1), (-1,-1), 10),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
]))
elements.append(Paragraph("1. System Capabilities and Limitations", heading_style))
elements.append(Paragraph("Hardware Summary", subheading_style))
elements.append(hardware_table)
elements.append(Spacer(1, 0.15*inch))

# Section 2: Performance Expectations
# Table cell style for LLM table
llm_cell_style = ParagraphStyle(
    'LLMTableCell',
    parent=styles['BodyText'],
    fontSize=9,
    leading=11,
    alignment=1  # Center
)

# Header style (bold, white text)
llm_header_style = ParagraphStyle(
    'LLMTableHeader',
    parent=styles['BodyText'],
    fontSize=9,
    leading=11,
    alignment=1,  # Center
    textColor=colors.whitesmoke,
    fontName='Helvetica-Bold'
)

llm_data = [
    [Paragraph("Model", llm_header_style), Paragraph("Quant", llm_header_style), Paragraph("VRAM", llm_header_style), Paragraph("Speed", llm_header_style), Paragraph("Notes", llm_header_style)],
    [Paragraph("Qwen2.5-Coder:7B", llm_cell_style), Paragraph("Q4_K_M", llm_cell_style), Paragraph("~4.5GB", llm_cell_style), Paragraph("15–25 t/s (GPU)", llm_cell_style), Paragraph("Best for technical troubleshooting", llm_cell_style)],
    [Paragraph("Llama 3.1:8B", llm_cell_style), Paragraph("Q4_K_M", llm_cell_style), Paragraph("~5GB", llm_cell_style), Paragraph("10–18 t/s (GPU)", llm_cell_style), Paragraph("Good balance of speed and capability", llm_cell_style)],
    [Paragraph("Gemma 2:9B", llm_cell_style), Paragraph("Q4_K_M", llm_cell_style), Paragraph("~6GB", llm_cell_style), Paragraph("10–15 t/s (GPU)", llm_cell_style), Paragraph("Requires >4GB VRAM", llm_cell_style)],
    [Paragraph("Qwen2.5-Coder:7B", llm_cell_style), Paragraph("Q4_K_M", llm_cell_style), Paragraph("~4.5GB", llm_cell_style), Paragraph("3–5 t/s (CPU)", llm_cell_style), Paragraph("Acceptable for non-urgent tasks", llm_cell_style)],
    [Paragraph("Llama 3.2:3B", llm_cell_style), Paragraph("Q4_K_M", llm_cell_style), Paragraph("~2GB", llm_cell_style), Paragraph("6–10 t/s (CPU)", llm_cell_style), Paragraph("Fastest CPU-only option", llm_cell_style)]
]
llm_table = Table(llm_data, colWidths=[1.4*inch, 0.8*inch, 0.7*inch, 1.2*inch, 1.9*inch])
llm_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e5c8a')),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 4),
    ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
    ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
]))

jellyfin_text = """• <b>GPU-accelerated transcoding</b>: Smooth HD streaming (~1.5–2GB VRAM usage)<br/>
• <b>CPU-only transcoding</b>: High CPU usage (~80–90%), may cause system slowdowns<br/>
• <b>Recommended</b>: Use GPU acceleration for optimal performance"""

elements.append(Paragraph("2. Performance Expectations", heading_style))
elements.append(Paragraph("LLM Inference Performance", subheading_style))
elements.append(llm_table)
elements.append(Spacer(1, 0.15*inch))
elements.append(Paragraph("Jellyfin Streaming Performance", subheading_style))
elements.append(Paragraph(jellyfin_text, body_style))
elements.append(Spacer(1, 0.15*inch))

# Section 3: Docker Configuration
config_text = """services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    environment:
      - OLLAMA_KV_CACHE_TYPE=q8_0
      - OLLAMA_NUM_PARALLEL=2
      - OLLAMA_MAX_LOADED_MODELS=2
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

# Wrap code in a table to apply background color
code_block = Preformatted(config_text, code_style)
code_table = Table([[code_block]], colWidths=[6*inch])
code_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
]))

elements.append(Paragraph("3. Docker Configuration Recommendations", heading_style))
elements.append(Paragraph("Ollama Container Configuration", subheading_style))
elements.append(code_table)
elements.append(Spacer(1, 0.15*inch))

# Section 4: Dual-Use Scenarios
conflict_text = """• <b>Jellyfin</b>: Uses ~1.5–2GB VRAM for HD transcoding<br/>
• <b>LLM</b>: Needs ~3.5GB VRAM for 7B Q4 model<br/>
• <b>Total VRAM needed</b>: ~5.5GB → <b>Exceeds available VRAM</b><br/>
• <b>Result</b>: <b>Cannot run both simultaneously</b> without VRAM conflicts"""

workarounds_data = [
    ["Scenario", "Solution", "Performance"],
    ["Jellyfin only", "Use GPU for transcoding", "Smooth HD streaming"],
    ["LLM only", "Use GPU for inference", "15–25 t/s"],
    ["Both active", "Use CPU-only LLM mode", "3–5 t/s (slow)"],
    ["Both active", "Switch to CPU-only Jellyfin", "80–90% CPU usage"]
]
workarounds_table = Table(workarounds_data, colWidths=[1.3*inch, 2.2*inch, 2*inch])
workarounds_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e5c8a')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 10),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
    ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ('FONTSIZE', (0,1), (-1,-1), 10),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
]))

elements.append(Paragraph("4. Dual-Use Scenarios and Workarounds", heading_style))
elements.append(Paragraph("Conflict: VRAM Limitation", subheading_style))
elements.append(Paragraph(conflict_text, body_style))
elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph("Workarounds", subheading_style))
elements.append(workarounds_table)
elements.append(Spacer(1, 0.15*inch))

# Section 5: Recommendations
# Table cell style for wrapping text
table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12
)

# Header style for upgrade table
upgrade_header_style = ParagraphStyle(
    'UpgradeHeader',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12,
    alignment=1,
    textColor=colors.whitesmoke,
    fontName='Helvetica-Bold'
)

upgrade_data = [
    [Paragraph("Component", upgrade_header_style), 
     Paragraph("Recommendation", upgrade_header_style), 
     Paragraph("Benefit", upgrade_header_style)],
    [Paragraph("GPU", table_cell_style), 
     Paragraph("Upgrade to <b>RTX 3060 (12GB)</b> or <b>RTX 4060 (8GB)</b>", table_cell_style), 
     Paragraph("Enables dual-use with 8GB+ VRAM", table_cell_style)],
    [Paragraph("CPU", table_cell_style), 
     Paragraph("Upgrade to <b>i7-12700K</b> or <b>i7-13700K</b>", table_cell_style), 
     Paragraph("Better multi-threading for dual workloads", table_cell_style)],
    [Paragraph("RAM", table_cell_style), 
     Paragraph("64GB DDR4 is sufficient", table_cell_style), 
     Paragraph("No need to upgrade", table_cell_style)]
]
upgrade_table = Table(upgrade_data, colWidths=[1.1*inch, 2.8*inch, 2.1*inch])
upgrade_table.setStyle(TableStyle([
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

elements.append(Paragraph("5. Recommendations for Long-Term Use", heading_style))
elements.append(Paragraph("Upgrade Path", subheading_style))
elements.append(upgrade_table)
elements.append(Spacer(1, 0.15*inch))

# Section 6: Summary
summary_cell_style = ParagraphStyle(
    'SummaryCell',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12
)

summary_header_style = ParagraphStyle(
    'SummaryHeader',
    parent=styles['BodyText'],
    fontSize=10,
    leading=12,
    alignment=1,
    textColor=colors.whitesmoke,
    fontName='Helvetica-Bold'
)

summary_data = [
    [Paragraph("Key Takeaway", summary_header_style), Paragraph("Details", summary_header_style)],
    [Paragraph("i5-11400 is sufficient", summary_cell_style), Paragraph("For single-use scenarios (either Jellyfin or LLM)", summary_cell_style)],
    [Paragraph("T4000 GPU is the bottleneck", summary_cell_style), Paragraph("4GB VRAM limits dual-use capabilities", summary_cell_style)],
    [Paragraph("GPU acceleration is essential", summary_cell_style), Paragraph("For LLM inference (20+ t/s)", summary_cell_style)],
    [Paragraph("CPU-only mode is slow", summary_cell_style), Paragraph("3–5 t/s, but usable for non-urgent tasks", summary_cell_style)],
    [Paragraph("Upgrade GPU to 8GB+ VRAM", summary_cell_style), Paragraph("For dual-use capability", summary_cell_style)],
    [Paragraph("Consider upgrading CPU", summary_cell_style), Paragraph("To i7-12700K or better for optimal performance", summary_cell_style)]
]
summary_table = Table(summary_data, colWidths=[2.2*inch, 3.8*inch])
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

elements.append(Paragraph("6. Summary of Key Takeaways", heading_style))
elements.append(summary_table)
elements.append(Spacer(1, 0.2*inch))

# Footer
elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph("Document Created On: Friday, January 23, 2026", body_style))
elements.append(Paragraph("Author: Leo (AI Assistant)", body_style))

# Build PDF
doc.build(elements)

print(f"PDF generated: {pdf_filename}")