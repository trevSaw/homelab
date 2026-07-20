from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

# Output Directory
OUTPUT_DIR = os.path.expanduser("~/my_projects/Personal/documents")

# Data
data = [
    ["Category", "Samsung Galaxy Z Flip 7", "Motorola Razr Ultra 60"],
    ["Main Display", "6.9\" AMOLED 2X, 120Hz", "7\" LTPO AMOLED, 165Hz"],
    ["Cover Display", "4.1\" Super AMOLED", "4\" LTPO AMOLED, 165Hz"],
    ["OS", "Android 16 (One UI 8), 7 updates", "Android 15 (Hello UX), 3 updates"],
    ["Chipset", "Exynos 2500", "Snapdragon 8 Elite"],
    ["RAM", "12GB", "16GB"],
    ["Storage", "256/512GB", "512GB"],
    ["Rear Cam", "50MP + 12MP UW", "50MP + 50MP UW"],
    ["Front Cam", "10MP", "50MP"],
    ["Battery", "4,300 mAh", "4,700 mAh"],
    ["Charging", "45W wired, 15W wireless", "68W wired, 30W wireless"],
    ["Price (¥)", "~160,000", "~170,000–190,000"]
]

# Create PDF
pdf_filename = os.path.join(OUTPUT_DIR, "flip_comparison.pdf")
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4

# Title
c.setFont("Helvetica-Bold", 16)
c.drawString(50, height - 50, "Samsung Galaxy Z Flip 7 vs Motorola Razr Ultra 60")

# Table
table = Table(data, colWidths=[1.8*inch, 2.3*inch, 2.3*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 12),
    ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ('GRID', (0,0), (-1,-1), 1, colors.black)
]))

table.wrapOn(c, width, height)
table.drawOn(c, 50, height - 250)

# Footer
c.setFont("Helvetica", 10)
c.drawString(50, 30, "Generated on: November 03, 2025")

c.save()
print(f"PDF generated: {pdf_filename}")   