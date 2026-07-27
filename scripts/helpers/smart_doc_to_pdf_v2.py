#!/usr/bin/env python3
"""
Smart Document to PDF Converter v2
===================================
Converts .docx files to formatted PDFs with AI enhancement and code detection.

New in v2:
    - Pygments-powered code block detection and language identification
    - Automatic syntax-aware formatting for code snippets
    - AI-powered theme selection and notes

Usage:
    python3 smart_doc_to_pdf_v2.py input.docx
    python3 smart_doc_to_pdf_v2.py input.docx --ai              # Use all AI features
    python3 smart_doc_to_pdf_v2.py input.docx --ai --code       # Detect code blocks
    python3 smart_doc_to_pdf_v2.py input.docx --ai --theme      # AI picks theme colors
    python3 smart_doc_to_pdf_v2.py input.docx --ai --notes      # Add AI notes
    python3 smart_doc_to_pdf_v2.py input.docx --title "Custom Title"
    python3 smart_doc_to_pdf_v2.py input.docx --author "Your Name"

Requirements:
    pip install pygments python-docx reportlab requests
"""

import os
import sys
import argparse
import json
import re
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

# Code Detection
try:
    from pygments.lexers import guess_lexer, get_lexer_by_name
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("Warning: Pygments not installed. Install with: pip install pygments")

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

# Language-specific code colors
CODE_THEMES = {
    "default": {
        "background": "#1e1e1e",
        "text": "#d4d4d4",
        "border": "#3c3c3c"
    },
    "python": {
        "background": "#1a2332",
        "text": "#e6db74",
        "border": "#306998"
    },
    "bash": {
        "background": "#2d2d2d",
        "text": "#50fa7b",
        "border": "#4EAA25"
    },
    "shell": {
        "background": "#2d2d2d",
        "text": "#50fa7b",
        "border": "#4EAA25"
    },
    "javascript": {
        "background": "#1e1e1e",
        "text": "#dcdcaa",
        "border": "#f7df1e"
    },
    "yaml": {
        "background": "#1f2937",
        "text": "#a5d6ff",
        "border": "#cb171e"
    },
    "json": {
        "background": "#1e1e1e",
        "text": "#ce9178",
        "border": "#5a5a5a"
    },
    "sql": {
        "background": "#1e2a3a",
        "text": "#9cdcfe",
        "border": "#336791"
    },
    "dockerfile": {
        "background": "#1e3a5f",
        "text": "#89ddff",
        "border": "#2496ed"
    },
    "config": {
        "background": "#2d2d2d",
        "text": "#b5cea8",
        "border": "#6a9955"
    }
}

# ============================================================================
# AI FUNCTIONS
# ============================================================================

def call_ollama(prompt, model=OLLAMA_MODEL, timeout=120):
    """Call local Ollama API"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}  # Lower temp for more consistent detection
            },
            timeout=timeout
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


def ai_detect_code_blocks(paragraphs):
    """
    Use AI to detect which paragraphs contain code and identify the language.
    Returns a dict mapping paragraph indices to detected language.
    """
    # Build context of all paragraphs for AI analysis
    para_texts = []
    for i, para in enumerate(paragraphs):
        text = para["text"][:200]  # Limit length for API
        para_texts.append(f"[{i}]: {text}")
    
    # Process in batches if needed
    batch_size = 30
    code_blocks = {}
    
    for batch_start in range(0, len(para_texts), batch_size):
        batch = para_texts[batch_start:batch_start + batch_size]
        batch_text = "\n".join(batch)
        
        prompt = f"""Analyze these numbered paragraphs from a document and identify which ones contain code or commands.

{batch_text}

For each paragraph that contains code, respond with its number and the programming language.
Respond ONLY with a JSON array like this (no other text):
[{{"index": 0, "language": "python"}}, {{"index": 5, "language": "bash"}}]

Common languages to detect:
- bash/shell: Terminal commands, apt install, systemctl, docker commands
- python: Python code with def, import, class, etc.
- yaml: YAML/config files with key: value format
- json: JSON data with curly braces and quotes
- sql: SQL queries with SELECT, INSERT, CREATE, etc.
- dockerfile: Docker instructions like FROM, RUN, COPY
- javascript: JS code with function, const, let, =>
- config: Config files, environment variables, INI format

If a paragraph is normal text (not code), do NOT include it.
If no paragraphs contain code, respond with: []
"""
        
        response = call_ollama(prompt)
        if response:
            try:
                # Extract JSON from response
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    detected = json.loads(json_match.group())
                    for item in detected:
                        idx = item.get("index")
                        lang = item.get("language", "default").lower()
                        if idx is not None:
                            # Adjust for batch offset
                            actual_idx = batch_start + idx
                            if actual_idx < len(paragraphs):
                                code_blocks[actual_idx] = lang
            except json.JSONDecodeError:
                pass
    
    return code_blocks


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
# CODE DETECTION (using Pygments + heuristics)
# ============================================================================

def is_prose(text):
    """Check if text looks like natural language prose."""
    text_lower = text.strip().lower()
    
    prose_indicators = [
        r'^(this|the|a|an|to|for|if|when|after|before|ensure|verify|note|see|check)\s',
        r'^step\s+\d+',  # "Step 1:"
        r'^\*\s+[A-Z]',  # "* The lowest..." bullet point with sentence
        r'^\d+\.\s+[A-Z]',  # "1. Install..." numbered step
        r'^summary$',
        r'^verify\s+operation',
        r'^suggestions\s+to',
        r'^(edit|paste|make|update|create)\s+(the|and|executable)',  # Instructions
    ]
    for pattern in prose_indicators:
        if re.match(pattern, text_lower):
            return True
    return False


def pygments_detect_code(text):
    """
    Use Pygments to detect if text is code and identify the language.
    Returns (is_code, language) tuple.
    """
    if not PYGMENTS_AVAILABLE:
        return False, None
    
    text_stripped = text.strip()
    
    # Skip very short text or obvious prose
    if len(text_stripped) < 5 or is_prose(text_stripped):
        return False, None
    
    try:
        lexer = guess_lexer(text_stripped)
        lang_name = lexer.name.lower()
        
        # Map Pygments lexer names to our language categories
        lang_map = {
            'bash': 'bash', 'shell': 'bash', 'console': 'bash', 'shell-session': 'bash',
            'python': 'python', 'python3': 'python',
            'yaml': 'yaml',
            'json': 'json',
            'sql': 'sql',
            'dockerfile': 'dockerfile', 'docker': 'dockerfile',
            'ini': 'config', 'properties': 'config', 'dosini': 'config',
            'javascript': 'javascript', 'js': 'javascript',
            'text': None,  # Plain text is not code
        }
        
        # Check confidence - Pygments returns a confidence score
        # For short snippets, it might misclassify, so we use our heuristics too
        detected_lang = lang_map.get(lang_name)
        
        # If Pygments says it's just "Text", it's probably not code
        if lang_name == 'text' or detected_lang is None:
            return False, None
        
        return True, detected_lang or lang_name
        
    except ClassNotFound:
        return False, None


def heuristic_detect_code(text):
    """
    Detect if a paragraph is code using heuristics.
    Returns detected language or None.
    """
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    
    # Skip if it looks like prose
    if is_prose(text_stripped):
        return None
    
    # STRONG code indicators - these are definitely code
    
    # Shebang
    if text_stripped.startswith('#!/'):
        return "bash"
    
    # Shell prompt
    if text_stripped.startswith('$ ') or text_stripped.startswith('# '):
        # But not if it's a heading like "# Summary"
        if not re.match(r'^#\s+[A-Z][a-z]+\s*$', text_stripped):
            return "bash"
    
    # Bash commands (must start with these)
    bash_commands = [
        'sudo', 'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'brew',
        'systemctl', 'service', 'journalctl',
        'docker', 'docker-compose', 'kubectl', 'podman',
        'git', 'npm', 'pip', 'python', 'python3', 'node',
        'nvidia-smi', 'nvcc', 'nvidia-ctk',
        'update-grub', 'update-initramfs', 'modprobe', 'lsmod',
        'wget', 'curl', 'echo', 'cat', 'chmod', 'chown', 'mkdir',
        'nano', 'vim', 'vi', 'tee', 'sed', 'awk', 'grep',
        'cpupower', 'powertop', 'hdparm', 'htop', 'sensors',
    ]
    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word in bash_commands:
        return "bash"
    
    # Config file assignments: VARIABLE="value" or VARIABLE=value
    if re.match(r'^[A-Z][A-Z0-9_]+=', text_stripped):
        return "config"
    
    # Systemd/INI section headers: [Unit], [Service], etc.
    if re.match(r'^\[(Unit|Service|Install|Timer|Socket|Mount|Path)\]', text_stripped):
        return "config"
    
    # Docker compose / YAML patterns
    yaml_patterns = [
        r'^(version|services|image|deploy|ports|volumes|devices|resources|reservations|capabilities|driver|count):\s*',
        r'^\s+[a-z_][a-z0-9_-]*:\s*',  # Indented key: value
        r'^\s+-\s+[a-z_]',              # Indented list item
        r'^\s+-\s+\d+:\d+',             # Port mapping: - 11434:11434
        r'^\s+-\s+/[a-z]',              # Volume mapping: - /opt/...
        r'^\s*-\s+\[?[a-z]+\]?$',       # Capability list: - [gpu]
    ]
    for pattern in yaml_patterns:
        if re.match(pattern, text_lower):
            return "yaml"
    
    # Comments that are clearly part of scripts
    if re.match(r'^#\s*(Install|Create|Add|Enable|Configure|Check|Test|Rebuild|Update)\s', text_stripped):
        return "bash"
    
    return None


def detect_code(text):
    """
    Combined code detection using both Pygments and heuristics.
    Heuristics take priority for short/ambiguous snippets.
    Returns detected language or None.
    """
    # First try heuristics (more reliable for command-line snippets)
    heuristic_result = heuristic_detect_code(text)
    if heuristic_result:
        return heuristic_result
    
    # Then try Pygments for more complex code
    if PYGMENTS_AVAILABLE:
        is_code, lang = pygments_detect_code(text)
        if is_code:
            return lang
    
    return None


def split_prose_and_code(paragraphs):
    """
    Split paragraphs that contain both prose and code.
    For example: 'Edit the file:\nGRUB_CMDLINE=...' becomes two paragraphs.
    Only splits when there's a clear code block (not just any detected code).
    """
    new_paragraphs = []
    
    for para in paragraphs:
        text = para["text"]
        style = para["style"]
        
        # Only try to split multi-line paragraphs
        lines = text.split('\n')
        
        if len(lines) > 1:
            # Look for clear prose:code pattern
            # (instruction ending with colon, followed by obvious code)
            current_prose = []
            current_code = []
            found_code_section = False
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Only detect STRONG code indicators (commands, not config values)
                is_strong_code = False
                if re.match(r'^(sudo|apt|systemctl|docker|git|nvidia-smi|update-grub|modprobe)\s', line_stripped.lower()):
                    is_strong_code = True
                elif re.match(r'^[A-Z][A-Z0-9_]+="', line_stripped):  # VARIABLE="value"
                    is_strong_code = True
                elif line_stripped.startswith('$ ') or line_stripped.startswith('# '):
                    is_strong_code = True
                
                if is_strong_code:
                    found_code_section = True
                    if current_prose:
                        # Save accumulated prose
                        new_paragraphs.append({
                            "text": '\n'.join(current_prose),
                            "style": style
                        })
                        current_prose = []
                    current_code.append(line_stripped)
                elif found_code_section and current_code:
                    # We were in code, check if this continues or is new prose
                    detected = detect_code(line_stripped)
                    if detected:
                        current_code.append(line_stripped)
                    else:
                        # End of code section
                        new_paragraphs.append({
                            "text": '\n'.join(current_code),
                            "style": "Code"
                        })
                        current_code = []
                        found_code_section = False
                        current_prose.append(line_stripped)
                else:
                    current_prose.append(line_stripped)
            
            # Save remaining content
            if current_prose:
                new_paragraphs.append({
                    "text": '\n'.join(current_prose),
                    "style": style
                })
            if current_code:
                new_paragraphs.append({
                    "text": '\n'.join(current_code),
                    "style": "Code"
                })
        else:
            # Single line paragraph, keep as is
            new_paragraphs.append(para)
    
    return new_paragraphs


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


def detect_structure(content, code_blocks=None, use_heuristics=False):
    """
    Detect document structure and convert to PDF content format.
    code_blocks: dict mapping paragraph indices to detected language
    """
    pdf_content = []
    paragraphs = content["paragraphs"]
    tables = content["tables"]
    table_index = 0
    
    if code_blocks is None:
        code_blocks = {}
    
    # Group consecutive code blocks of the same language
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i]
        text = para["text"]
        style = para["style"].lower()
        
        # Check if this paragraph was pre-marked as code (from split_prose_and_code)
        if style == "code":
            detected_lang = detect_code(text) or "config"
        else:
            # Check if this paragraph is detected as code by AI
            detected_lang = code_blocks.get(i)
            
            # Fallback to Pygments + heuristic detection if enabled
            if detected_lang is None and use_heuristics:
                detected_lang = detect_code(text)
        
        if detected_lang:
            # Collect consecutive code blocks
            code_lines = [text]
            j = i + 1
            while j < len(paragraphs):
                next_text = paragraphs[j]["text"]
                next_style = paragraphs[j]["style"].lower()
                next_lang = code_blocks.get(j)
                if next_lang is None and use_heuristics:
                    next_lang = detect_code(next_text)
                
                # For YAML: keep grouping if line is indented or looks like YAML continuation
                if detected_lang == "yaml":
                    is_yaml_continuation = (
                        next_text.startswith(' ') or  # Indented
                        next_text.startswith('\t') or  # Tab indented
                        next_text.startswith('-') or  # List item
                        next_lang == "yaml" or
                        re.match(r'^[a-z_][a-z0-9_-]*:', next_text.lower())  # key:
                    )
                    if is_yaml_continuation:
                        code_lines.append(next_text)
                        j += 1
                        continue
                
                # For other languages: group same language
                if next_lang == detected_lang:
                    code_lines.append(next_text)
                    j += 1
                # Also group if next line is marked as code style (from pre-processing)
                elif next_style == "code" and next_lang:
                    code_lines.append(next_text)
                    j += 1
                else:
                    break
            
            pdf_content.append({
                "type": "code",
                "content": "\n".join(code_lines),
                "language": detected_lang
            })
            i = j
            continue
        
        # Detect title (first paragraph or Heading 1)
        if i == 0 or "title" in style or "heading 1" in style:
            if i == 0:
                pdf_content.append({"type": "title", "content": text})
                i += 1
                continue
        
        # Detect headings
        if "heading" in style:
            if "2" in style or "heading2" in style:
                pdf_content.append({"type": "subheading", "content": text})
            else:
                pdf_content.append({"type": "heading", "content": text})
            i += 1
            continue
        
        # Detect section markers
        if text.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            pdf_content.append({"type": "heading", "content": text})
            i += 1
            continue
        
        if "===" in text or "---" in text:
            i += 1
            continue
        
        # Detect bullet lists
        if text.startswith(("•", "-", "*", "·")) and not text.startswith("---"):
            pdf_content.append({"type": "paragraph", "content": text})
            i += 1
            continue
        
        # Check for table triggers
        if "table" in text.lower() or text.endswith(":"):
            pdf_content.append({"type": "paragraph", "content": text})
            if table_index < len(tables):
                pdf_content.append({
                    "type": "table",
                    "content": tables[table_index],
                    "colWidths": calculate_col_widths(tables[table_index])
                })
                table_index += 1
            i += 1
            continue
        
        # Regular paragraph
        pdf_content.append({"type": "paragraph", "content": text})
        i += 1
    
    # Add remaining tables
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
    total_width = 7.5  # Full width with 0.5" margins
    
    max_lengths = [0] * num_cols
    for row in table_data:
        for i, cell in enumerate(row):
            if i < num_cols:
                max_lengths[i] = max(max_lengths[i], len(str(cell)))
    
    total_length = sum(max_lengths) or 1
    widths = [(length / total_length) * total_width for length in max_lengths]
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
            textColor=colors.HexColor('#d4d4d4'),
            spaceAfter=0,
            spaceBefore=0
        ),
        'code_label': ParagraphStyle(
            'CodeLabel',
            parent=base_styles['BodyText'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            spaceAfter=2
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


def wrap_code_lines(text, max_chars=105):
    """Wrap long lines in code blocks to fit within the box"""
    wrapped_lines = []
    for line in text.split('\n'):
        if len(line) <= max_chars:
            wrapped_lines.append(line)
        else:
            # Wrap long lines with continuation indent
            while len(line) > max_chars:
                # Try to break at a space or after certain characters
                break_point = max_chars
                for char in [' ', '/', '\\', '-', '_', ',', ';', ':', '=']:
                    last_pos = line[:max_chars].rfind(char)
                    if last_pos > max_chars // 2:
                        break_point = last_pos + 1
                        break
                
                wrapped_lines.append(line[:break_point])
                line = '  ' + line[break_point:]  # Indent continuation
            if line.strip():
                wrapped_lines.append(line)
    return '\n'.join(wrapped_lines)


def create_code_block(code_text, language="default"):
    """Create a styled code block with language-specific colors"""
    theme = CODE_THEMES.get(language, CODE_THEMES["default"])
    
    # Wrap long lines to prevent overflow
    wrapped_text = wrap_code_lines(code_text, max_chars=85)
    
    # Create the code style with language-specific colors
    code_style = ParagraphStyle(
        'DynamicCode',
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor(theme["text"]),
    )
    
    code_block = Preformatted(wrapped_text, code_style)
    
    # Create table with language-specific background (7.5 inches = full width with 0.5" margins)
    code_table = Table([[code_block]], colWidths=[7.5*inch])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(theme["background"])),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(theme["border"])),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),  # Rounded corners like modern code blocks
    ]))
    
    return code_table, language


def create_table(data, col_widths, styles, theme):
    """Create a formatted table"""
    primary = theme.get("primary", "#1f4788")
    accent = theme.get("accent", "#f0f0f0")
    
    header_row = [Paragraph(str(cell), styles['table_header']) for cell in data[0]]
    
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
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=letter, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
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
            language = item.get("language", "default")
            # Add language label
            if language != "default":
                lang_display = language.upper()
                elements.append(Paragraph(f"[{lang_display}]", styles['code_label']))
            code_table, _ = create_code_block(content, language)
            elements.append(code_table)
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
        description="Convert .docx to formatted PDF with AI enhancement and code detection (v2)"
    )
    parser.add_argument("input_file", help="Path to .docx file")
    parser.add_argument("--output", "-o", help="Output PDF path (default: auto-generated)")
    parser.add_argument("--title", "-t", help="Custom document title")
    parser.add_argument("--author", "-a", default="Trevor Sawyer", help="Document author")
    parser.add_argument("--ai", action="store_true", help="Use AI features (enables all AI options by default)")
    parser.add_argument("--code", action="store_true", help="Use AI to detect code blocks")
    parser.add_argument("--theme", action="store_true", help="Let AI pick theme colors")
    parser.add_argument("--notes", action="store_true", help="Add AI-generated notes")
    parser.add_argument("--heuristics", action="store_true", help="Use heuristic code detection (no AI needed)")
    
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
    
    # Detect title (before splitting)
    title = args.title
    if not title and content["paragraphs"]:
        title = content["paragraphs"][0]["text"]
    title = title or "Untitled Document"
    print(f"   Title: {title}")
    
    # Pre-process: Split paragraphs that mix prose and code (only for multi-line paragraphs)
    original_count = len(content["paragraphs"])
    content["paragraphs"] = split_prose_and_code(content["paragraphs"])
    if len(content["paragraphs"]) != original_count:
        print(f"   Split mixed paragraphs: {original_count} → {len(content['paragraphs'])}")
    
    # Get theme
    theme = DEFAULT_COLORS.copy()
    if args.ai and args.theme:
        print("\n🤖 Asking AI for theme suggestions...")
        theme = ai_suggest_theme(content["raw_text"])
    
    # Detect code blocks
    code_blocks = {}
    use_heuristics = args.heuristics
    
    if args.ai and args.code:
        print("\n🤖 Analyzing document for code blocks...")
        code_blocks = ai_detect_code_blocks(content["paragraphs"])
        if code_blocks:
            # Summarize detections
            lang_counts = {}
            for lang in code_blocks.values():
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            summary = ", ".join([f"{count} {lang}" for lang, count in lang_counts.items()])
            print(f"✓ Detected code blocks: {summary}")
        else:
            print("✓ No code blocks detected by AI, falling back to heuristics")
            use_heuristics = True
    
    # Get AI notes
    ai_notes = None
    if args.ai and args.notes:
        print("\n🤖 Generating AI enhancement notes...")
        ai_notes = ai_enhance_content(content["raw_text"], title)
    
    # Parse content
    print("\n📝 Parsing document structure...")
    pdf_content = detect_structure(content, code_blocks, use_heuristics)
    
    # Count detected code blocks in output
    code_count = sum(1 for item in pdf_content if item.get("type") == "code")
    if code_count > 0:
        print(f"   Found {code_count} code block(s)")
    
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
        if args.theme:
            print(f"   Theme: {theme.get('theme_name', 'Custom')}")
        if args.code or use_heuristics:
            print(f"   Code blocks: {code_count} detected")


if __name__ == "__main__":
    main()
