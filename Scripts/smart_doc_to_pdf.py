#!/usr/bin/env python3
"""
Smart Document to PDF Converter
================================
Converts .docx files to formatted PDFs with optional AI enhancement.

Usage:
    python3 smart_doc_to_pdf.py input.docx
    python3 smart_doc_to_pdf.py input.docx --ai          # Use AI to enhance
    python3 smart_doc_to_pdf.py input.docx --ai --theme  # AI picks theme colors
    python3 smart_doc_to_pdf.py input.docx --title "Custom Title"
    python3 smart_doc_to_pdf.py input.docx --author "Your Name"
"""

import os
import sys
import argparse
import json
import requests
from datetime import datetime
from functools import partial

# PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib import colors

# Document Reading
from docx import Document

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = os.path.expanduser("~/my_projects/Personal/documents")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b-instruct-q4_K_M"  # Fast, lightweight model

# Default colors
DEFAULT_COLORS = {
    "primary": "#1f4788",
    "secondary": "#2e5c8a", 
    "tertiary": "#3d7ba8",
    "accent": "#f0f0f0"
}

# ============================================================================
# AI ENHANCEMENT FUNCTIONS
# ============================================================================

def call_ollama(prompt, model=OLLAMA_MODEL):
    """Call local Ollama API"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"Warning: Ollama returned status {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("Warning: Could not connect to Ollama. Is it running?")
        return None
    except Exception as e:
        print(f"Warning: Ollama error: {e}")
        return None


def ai_suggest_theme(content_text):
    """Ask AI to suggest a color theme based on content"""
    prompt = f"""Analyze this document content and suggest a color theme.

Content preview:
{content_text[:1500]}

Respond with ONLY a JSON object (no markdown, no explanation) in this exact format:
{{"primary": "#XXXXXX", "secondary": "#XXXXXX", "tertiary": "#XXXXXX", "accent": "#XXXXXX", "theme_name": "name"}}

Choose colors that match the document's topic/mood. Examples:
- Technical docs: blues and grays
- Star Wars Sith: dark reds and blacks
- Nature/Environment: greens
- Finance: navy and gold
- Medical: teal and white
"""
    
    response = call_ollama(prompt)
    if response:
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                theme = json.loads(json_match.group())
                print(f"✓ AI suggested theme: {theme.get('theme_name', 'Custom')}")
                return theme
        except json.JSONDecodeError:
            pass
    
    print("✓ Using default theme")
    return DEFAULT_COLORS


def ai_enhance_content(content_text, doc_title):
    """Ask AI to suggest enhancements for the document"""
    prompt = f"""Analyze this document and suggest enhancements.

Title: {doc_title}
Content:
{content_text[:3000]}

Suggest 2-3 brief, relevant additions that would improve this document. 
Keep each suggestion to 1-2 sentences.
Format as a simple bullet list.
Be specific to the document's topic.
"""
    
    response = call_ollama(prompt)
    if response:
        print("✓ AI generated enhancement suggestions")
        return response.strip()
    return None


# ============================================================================
# DOCUMENT PARSING
# ============================================================================

def read_docx(filepath):
    """Read a .docx file and extract content"""
    doc = Document(filepath)
    
    content = {
        "paragraphs": [],
        "tables": [],
        "raw_text": ""
    }
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content["paragraphs"].append({
                "text": text,
                "style": para.style.name if para.style else "Normal"
            })
            content["raw_text"] += text + "\n"
    
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            table_data.append(row_data)
        if table_data:
            content["tables"].append(table_data)
    
    return content


def detect_structure(content):
    """Detect document structure and convert to PDF content format"""
    pdf_content = []
    paragraphs = content["paragraphs"]
    tables = content["tables"]
    table_index = 0
    
    for i, para in enumerate(paragraphs):
        text = para["text"]
        style = para["style"].lower()
        
        # Detect title (first paragraph or Heading 1)
        if i == 0 or "title" in style or "heading 1" in style:
            if i == 0:
                pdf_content.append({"type": "title", "content": text})
                continue
        
        # Detect headings
        if "heading" in style:
            if "2" in style or "heading2" in style:
                pdf_content.append({"type": "subheading", "content": text})
            else:
                pdf_content.append({"type": "heading", "content": text})
            continue
        
        # Detect section markers (numbered sections, lines with === or ---)
        if text.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            pdf_content.append({"type": "heading", "content": text})
            continue
        
        if "===" in text or "---" in text:
            continue  # Skip separator lines
        
        # Detect bullet lists
        if text.startswith(("•", "-", "*", "·")):
            # Collect consecutive bullet points
            bullets = [text.lstrip("•-*· ")]
            continue
        
        # Detect tables (check if next content should be a table)
        if "table" in text.lower() or text.endswith(":"):
            pdf_content.append({"type": "paragraph", "content": text})
            if table_index < len(tables):
                pdf_content.append({
                    "type": "table",
                    "content": tables[table_index],
                    "colWidths": calculate_col_widths(tables[table_index])
                })
                table_index += 1
            continue
        
        # Regular paragraph
        pdf_content.append({"type": "paragraph", "content": text})
    
    # Add remaining tables at the end if any
    while table_index < len(tables):
        pdf_content.append({
            "type": "table",
            "content": tables[table_index],
            "colWidths": calculate_col_widths(tables[table_index])
        })
        table_index += 1
    
    return pdf_content


def calculate_col_widths(table_data):
    """Calculate appropriate column widths based on content"""
    if not table_data or not table_data[0]:
        return [2]
    
    num_cols = len(table_data[0])
    total_width = 6.0  # inches
    
    # Calculate max content length per column
    max_lengths = [0] * num_cols
    for row in table_data:
        for i, cell in enumerate(row):
            if i < num_cols:
                max_lengths[i] = max(max_lengths[i], len(str(cell)))
    
    # Distribute width proportionally
    total_length = sum(max_lengths) or 1
    widths = [(length / total_length) * total_width for length in max_lengths]
    
    # Ensure minimum width
    widths = [max(w, 0.8) for w in widths]
    
    return widths


# ============================================================================
# PDF GENERATION
# ============================================================================

def add_page_footer(canvas, doc, creation_date):
    """Add footer with creation date to each page"""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    page_width = letter[0]
    canvas.drawCentredString(page_width / 2, 0.35 * inch, f"Created: {creation_date}")
    canvas.drawRightString(page_width - 0.5 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def get_styles(theme):
    """Generate styles based on theme colors"""
    base_styles = getSampleStyleSheet()
    
    return {
        'title': ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor(theme.get("primary", "#1f4788")),
            spaceAfter=4,
            alignment=1
        ),
        'author': ParagraphStyle(
            'AuthorStyle',
            parent=base_styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=16,
            alignment=1
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=base_styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor(theme.get("secondary", "#2e5c8a")),
            spaceAfter=8,
            spaceBefore=12,
            keepWithNext=True
        ),
        'subheading': ParagraphStyle(
            'CustomSubHeading',
            parent=base_styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor(theme.get("tertiary", "#3d7ba8")),
            spaceAfter=6,
            spaceBefore=6,
            keepWithNext=True
        ),
        'body': ParagraphStyle(
            'CustomBody',
            parent=base_styles['BodyText'],
            fontSize=10,
            spaceAfter=8
        ),
        'code': ParagraphStyle(
            'CodeBlock',
            parent=base_styles['Code'],
            fontName='Courier',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=0,
            spaceBefore=0
        ),
        'table_cell': ParagraphStyle(
            'TableCell',
            parent=base_styles['BodyText'],
            fontSize=10,
            leading=12
        ),
        'table_header': ParagraphStyle(
            'TableHeader',
            parent=base_styles['BodyText'],
            fontSize=10,
            leading=12,
            alignment=1,
            textColor=colors.whitesmoke,
            fontName='Helvetica-Bold'
        )
    }


def create_code_block(code_text, code_style):
    """Create a styled code block"""
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


def create_table(data, col_widths, styles, theme):
    """Create a formatted table"""
    primary = theme.get("primary", "#1f4788")
    accent = theme.get("accent", "#f0f0f0")
    
    # Process header row
    header_row = [Paragraph(str(cell), styles['table_header']) for cell in data[0]]
    
    # Process data rows
    data_rows = []
    for row in data[1:]:
        processed_row = [Paragraph(str(cell), styles['table_cell']) for cell in row]
        data_rows.append(processed_row)
    
    table_data = [header_row] + data_rows
    widths = [w * inch for w in col_widths]
    
    table = Table(table_data, colWidths=widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(primary)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(accent)),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    return table


def generate_pdf(pdf_content, output_path, title, author, theme, ai_notes=None):
    """Generate the PDF document"""
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = get_styles(theme)
    
    for item in pdf_content:
        content_type = item.get("type")
        content = item.get("content", "")
        
        if content_type == "title":
            elements.append(Paragraph(content, styles['title']))
            elements.append(Paragraph(f"Author: {author}", styles['author']))
        
        elif content_type == "heading":
            elements.append(Paragraph(content, styles['heading']))
        
        elif content_type == "subheading":
            elements.append(Paragraph(content, styles['subheading']))
        
        elif content_type == "paragraph":
            elements.append(Paragraph(content, styles['body']))
        
        elif content_type == "bullet_list":
            for bullet in content:
                elements.append(Paragraph(f"• {bullet}", styles['body']))
            elements.append(Spacer(1, 0.1*inch))
        
        elif content_type == "table":
            col_widths = item.get("colWidths", [2, 2, 2])
            table = create_table(content, col_widths, styles, theme)
            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))
        
        elif content_type == "code":
            elements.append(create_code_block(content, styles['code']))
            elements.append(Spacer(1, 0.15*inch))
        
        elif content_type == "page_break":
            elements.append(PageBreak())
        
        elif content_type == "spacer":
            elements.append(Spacer(1, item.get("height", 0.2) * inch))
    
    # Add AI notes if provided
    if ai_notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("AI-Generated Notes", styles['heading']))
        elements.append(Paragraph(ai_notes.replace("\n", "<br/>"), styles['body']))
    
    # Build with footer
    creation_date = datetime.now().strftime('%B %d, %Y')
    footer_func = partial(add_page_footer, creation_date=creation_date)
    doc.build(elements, onFirstPage=footer_func, onLaterPages=footer_func)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert .docx to formatted PDF with optional AI enhancement"
    )
    parser.add_argument("input_file", help="Path to .docx file")
    parser.add_argument("--output", "-o", help="Output PDF path (default: auto-generated)")
    parser.add_argument("--title", "-t", help="Custom document title")
    parser.add_argument("--author", "-a", default="Trevor Sawyer", help="Document author")
    parser.add_argument("--ai", action="store_true", help="Use AI to enhance document")
    parser.add_argument("--theme", action="store_true", help="Let AI pick theme colors (requires --ai)")
    parser.add_argument("--notes", action="store_true", help="Add AI-generated notes (requires --ai)")
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)
    
    if not args.input_file.endswith(".docx"):
        print("Error: Input file must be a .docx file")
        sys.exit(1)
    
    print(f"\n📄 Reading: {args.input_file}")
    
    # Read document
    content = read_docx(args.input_file)
    print(f"   Found {len(content['paragraphs'])} paragraphs, {len(content['tables'])} tables")
    
    # Detect title
    title = args.title
    if not title and content["paragraphs"]:
        title = content["paragraphs"][0]["text"]
    title = title or "Untitled Document"
    print(f"   Title: {title}")
    
    # Get theme
    theme = DEFAULT_COLORS.copy()
    if args.ai and args.theme:
        print("\n🤖 Asking AI for theme suggestions...")
        theme = ai_suggest_theme(content["raw_text"])
    
    # Get AI notes
    ai_notes = None
    if args.ai and args.notes:
        print("\n🤖 Generating AI enhancement notes...")
        ai_notes = ai_enhance_content(content["raw_text"], title)
    
    # Parse content
    print("\n📝 Parsing document structure...")
    pdf_content = detect_structure(content)
    
    # Generate output path
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        safe_name = base_name.replace(":", "_").replace(" ", "_")
        output_path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate PDF
    print(f"\n📄 Generating PDF...")
    generate_pdf(pdf_content, output_path, title, args.author, theme, ai_notes)
    
    print(f"\n✅ PDF generated: {output_path}")
    if args.ai:
        print(f"   Theme: {theme.get('theme_name', 'Custom')}")


if __name__ == "__main__":
    main()
