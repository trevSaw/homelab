from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib import colors
from datetime import datetime
from functools import partial

# ============================================================================
# EASY PDF CONFIGURATION - EDIT THESE VARIABLES
# ============================================================================

# Output Directory (where PDFs will be saved)
import os
OUTPUT_DIR = os.path.expanduser("~/my_projects/Personal/documents")

# PDF Output Filename
PDF_FILENAME = os.path.join(OUTPUT_DIR, "my_document.pdf")

# Document Title
DOCUMENT_TITLE = "My Document Title"

# Document Author
DOCUMENT_AUTHOR = "Your Name"

# Color Scheme (Hex Colors)
PRIMARY_COLOR = "#1f4788"
SECONDARY_COLOR = "#2e5c8a"
TERTIARY_COLOR = "#3d7ba8"
ACCENT_COLOR = "#f0f0f0"

# ============================================================================
# DOCUMENT CONTENT - COPY AND PASTE YOUR CONTENT HERE
# ============================================================================

DOCUMENT_CONTENT = [
    {
        "type": "title",
        "content": "My Document Title"
    },
    {
        "type": "paragraph",
        "content": "This is an introductory paragraph. You can add as much text as you need here. It will automatically wrap to fit the page."
    },
    {
        "type": "heading",
        "content": "1. First Section"
    },
    {
        "type": "subheading",
        "content": "Subsection 1.1"
    },
    {
        "type": "paragraph",
        "content": "This is a paragraph under the subsection. You can add multiple paragraphs by adding more entries to the DOCUMENT_CONTENT list."
    },
    {
        "type": "paragraph",
        "content": "This is another paragraph. Notice how easy it is to add content!"
    },
    {
        "type": "subheading",
        "content": "Subsection 1.2"
    },
    {
        "type": "paragraph",
        "content": "More content goes here. You can mix and match different content types."
    },
    {
        "type": "table",
        "content": [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
            ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"]
        ],
        "colWidths": [1.5, 2, 2.5]
    },
    {
        "type": "heading",
        "content": "2. Second Section"
    },
    {
        "type": "paragraph",
        "content": "You can add as many sections as you need. Just keep adding entries to the DOCUMENT_CONTENT list."
    },
    {
        "type": "code",
        "content": "# This is a code block\nprint('Hello, World!')\nfor i in range(5):\n    print(i)"
    },
    {
        "type": "paragraph",
        "content": "Code blocks are great for technical documentation."
    },
    {
        "type": "spacer",
        "height": 0.2
    },
    {
        "type": "heading",
        "content": "3. Third Section"
    },
    {
        "type": "paragraph",
        "content": "This section demonstrates bullet lists."
    },
    {
        "type": "bullet_list",
        "content": [
            "First bullet point",
            "Second bullet point",
            "Third bullet point",
            "Fourth bullet point"
        ]
    },
    {
        "type": "paragraph",
        "content": "Bullet lists are easy to add too!"
    },
    {
        "type": "page_break"
    },
    {
        "type": "heading",
        "content": "4. Fourth Section (New Page)"
    },
    {
        "type": "paragraph",
        "content": "This content appears on a new page thanks to the page_break entry above."
    }
]

# ============================================================================
# PAGE FOOTER FUNCTION
# ============================================================================

def add_page_footer(canvas, doc, creation_date):
    """Add footer with creation date to each page"""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    # Draw date at bottom center
    page_width = letter[0]
    canvas.drawCentredString(page_width / 2, 0.35 * inch, f"Created: {creation_date}")
    # Draw page number at bottom right
    canvas.drawRightString(page_width - 0.5 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


# ============================================================================
# STYLE DEFINITIONS - CUSTOMIZE FONTS AND COLORS HERE
# ============================================================================

def get_styles(primary_color, secondary_color, tertiary_color):
    """Generate custom styles based on color scheme"""
    base_styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=base_styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor(primary_color),
        spaceAfter=4,
        alignment=1  # Center alignment
    )
    
    author_style = ParagraphStyle(
        'AuthorStyle',
        parent=base_styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=16,
        alignment=1  # Center alignment
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=base_styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(secondary_color),
        spaceAfter=8,
        spaceBefore=12,
        keepWithNext=True  # Keeps heading with following content
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=base_styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor(tertiary_color),
        spaceAfter=6,
        spaceBefore=6,
        keepWithNext=True  # Keeps subheading with following content
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=base_styles['BodyText'],
        fontSize=10,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=base_styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=0,
        spaceBefore=0
    )

    # Table cell style for wrapping text
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=base_styles['BodyText'],
        fontSize=10,
        leading=12
    )

    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=base_styles['BodyText'],
        fontSize=10,
        leading=12,
        alignment=1,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )

    return {
        'title': title_style,
        'author': author_style,
        'heading': heading_style,
        'subheading': subheading_style,
        'body': body_style,
        'code': code_style,
        'table_cell': table_cell_style,
        'table_header': table_header_style
    }


def create_code_block(code_text, code_style):
    """Helper function to create a styled code block with background"""
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


def create_table(data, col_widths, styles, primary_color, accent_color):
    """Helper function to create a properly formatted table with wrapped text"""
    # Process header row
    header_row = [Paragraph(str(cell), styles['table_header']) for cell in data[0]]
    
    # Process data rows
    data_rows = []
    for row in data[1:]:
        processed_row = [Paragraph(str(cell), styles['table_cell']) for cell in row]
        data_rows.append(processed_row)
    
    # Combine header and data
    table_data = [header_row] + data_rows
    
    # Convert column widths to inches
    widths = [w * inch for w in col_widths]
    
    table = Table(table_data, colWidths=widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(primary_color)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(accent_color)),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    return table


# ============================================================================
# GENERATE PDF
# ============================================================================

# Create PDF
doc = SimpleDocTemplate(PDF_FILENAME, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

# Container for PDF elements
elements = []

# Define styles
styles = get_styles(PRIMARY_COLOR, SECONDARY_COLOR, TERTIARY_COLOR)

# Add content
for item in DOCUMENT_CONTENT:
    content_type = item["type"]
    
    if content_type == "title":
        elements.append(Paragraph(item["content"], styles['title']))
        elements.append(Paragraph(f"Author: {DOCUMENT_AUTHOR}", styles['author']))
    
    elif content_type == "paragraph":
        elements.append(Paragraph(item["content"], styles['body']))
    
    elif content_type == "heading":
        elements.append(Paragraph(item["content"], styles['heading']))
    
    elif content_type == "subheading":
        elements.append(Paragraph(item["content"], styles['subheading']))
    
    elif content_type == "table":
        col_widths = item.get("colWidths", [2, 2, 2])
        table = create_table(item["content"], col_widths, styles, PRIMARY_COLOR, ACCENT_COLOR)
        elements.append(table)
        elements.append(Spacer(1, 0.15*inch))
    
    elif content_type == "code":
        elements.append(create_code_block(item["content"], styles['code']))
        elements.append(Spacer(1, 0.15*inch))
    
    elif content_type == "bullet_list":
        for bullet_item in item["content"]:
            elements.append(Paragraph(f"• {bullet_item}", styles['body']))
        elements.append(Spacer(1, 0.1*inch))
    
    elif content_type == "spacer":
        elements.append(Spacer(1, item["height"]*inch))
    
    elif content_type == "page_break":
        elements.append(PageBreak())

# Build PDF with page footer
creation_date = datetime.now().strftime('%B %d, %Y')
footer_func = partial(add_page_footer, creation_date=creation_date)
doc.build(elements, onFirstPage=footer_func, onLaterPages=footer_func)

print(f"PDF generated: {PDF_FILENAME}")
