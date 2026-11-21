"""
Generates synthetic enterprise PDF dataset:
1. Master Services Agreement (MSA_Acme_Cyberdyne_2024.pdf)
2. Statement of Work (SOW_Cloud_Infrastructure.pdf)
3. Compliant Invoice (INV_2024_081_Compliant.pdf)
4. Disputed Overcharge Invoice (INV_2024_099_Disputed.pdf)
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#1e293b'),
    spaceAfter=14
)

h2_style = ParagraphStyle(
    'DocH2',
    parent=styles['Heading2'],
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#0f172a'),
    spaceBefore=10,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#334155'),
    spaceAfter=8
)

table_header_style = ParagraphStyle(
    'TH',
    parent=styles['Normal'],
    fontSize=9,
    leading=11,
    fontName='Helvetica-Bold',
    textColor=colors.white
)

table_cell_style = ParagraphStyle(
    'TC',
    parent=styles['Normal'],
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#1e293b')
)

def build_msa():
    filepath = os.path.join(OUTPUT_DIR, "MSA_Acme_Cyberdyne_2024.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("MASTER SERVICES AGREEMENT", title_style))
    story.append(Paragraph("<b>Contract ID:</b> MSA-2024-ACME-CYBER | <b>Effective Date:</b> January 15, 2024", body_style))
    story.append(Paragraph("This Master Services Agreement ('Agreement') is entered into by and between <b>Acme Corporation</b> ('Client'), with offices at 100 Enterprise Way, Suite 400, New York, NY 10001, and <b>Cyberdyne Systems Inc.</b> ('Vendor'), with offices at 2049 Silicon Parkway, San Jose, CA 95134.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("SECTION 1: SCOPE OF SERVICES & STATEMENTS OF WORK", h2_style))
    story.append(Paragraph("1.1 Vendor shall provide cloud architecture, migration, and software engineering services as described in mutually executed Statements of Work ('SOW'). Each SOW shall reference this Agreement and specify deliverables, delivery milestones, acceptance criteria, and project schedules.", body_style))

    story.append(Paragraph("SECTION 2: FEES, INVOICING & PAYMENT TERMS", h2_style))
    story.append(Paragraph("2.1 <b>Invoicing Schedule:</b> Vendor shall invoice Client upon the formal written acceptance of milestone deliverables defined in the applicable SOW.", body_style))
    story.append(Paragraph("2.2 <b>Payment Terms (Net-30):</b> Undisputed invoices shall be payable within <b>thirty (30) calendar days</b> from the date of Client's receipt of a valid itemized invoice ('Net-30').", body_style))
    story.append(Paragraph("2.3 <b>Late Payment Penalty Cap:</b> If Client fails to pay any undisputed sum when due, simple interest may accrue at a rate not to exceed <b>one and one-half percent (1.5%) per month</b>, or the maximum rate permitted by law, whichever is less. Any invoice imposing penalty charges exceeding 1.5% per month is null and void.", body_style))

    story.append(Paragraph("SECTION 3: INTELLECTUAL PROPERTY & OWNERSHIP", h2_style))
    story.append(Paragraph("3.1 <b>Work Product Ownership:</b> All software code, configuration scripts, documentation, and technical deliverables developed under any SOW shall constitute 'work made for hire' and remain the sole and exclusive property of Client upon payment.", body_style))

    story.append(Paragraph("SECTION 4: INDEMNIFICATION & LIMITATION OF LIABILITY", h2_style))
    story.append(Paragraph("4.1 <b>Vendor Indemnification:</b> Vendor shall defend, indemnify, and hold harmless Client against any third-party claims alleging that deliverables infringe any patent, copyright, or trade secret. Indemnification obligations under this Section 4.1 are <b>uncapped</b>.", body_style))
    story.append(Paragraph("4.2 <b>Aggregate Liability Cap:</b> Except for breach of Section 4.1 (Indemnification) or gross negligence, each party's aggregate cumulative liability under this Agreement shall not exceed the <b>total fees actually paid by Client in the preceding twelve (12) months</b>.", body_style))

    story.append(Paragraph("SECTION 5: TERMINATION", h2_style))
    story.append(Paragraph("5.1 <b>Termination for Convenience:</b> Client may terminate this Agreement or any active SOW at any time without penalty upon providing <b>thirty (30) calendar days advance written notice</b> to Vendor.", body_style))
    story.append(Paragraph("5.2 <b>Termination for Material Breach:</b> Either party may terminate immediately upon written notice if the other party breaches any material term and fails to cure such breach within fifteen (15) business days.", body_style))

    story.append(Paragraph("SECTION 6: GOVERNING LAW & VENUE", h2_style))
    story.append(Paragraph("6.1 This Agreement shall be governed by, and construed in accordance with, the laws of the <b>State of Delaware</b>, without regard to conflict of law principles.", body_style))

    doc.build(story)
    print(f"Generated: {filepath}")

def build_sow():
    filepath = os.path.join(OUTPUT_DIR, "SOW_Cloud_Infrastructure.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("STATEMENT OF WORK #01: CLOUD INFRASTRUCTURE", title_style))
    story.append(Paragraph("<b>SOW Number:</b> SOW-2024-01 | <b>Master Agreement:</b> MSA-2024-ACME-CYBER", body_style))
    story.append(Paragraph("This Statement of Work specifies the milestones, deliverables, and fixed-fee budget agreed between Acme Corporation and Cyberdyne Systems Inc.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("APPROVED PROJECT MILESTONES & BUDGET", h2_style))

    table_data = [
        [
            Paragraph("Milestone #", table_header_style),
            Paragraph("Deliverable Description", table_header_style),
            Paragraph("Target Date", table_header_style),
            Paragraph("Fixed Price (USD)", table_header_style)
        ],
        [
            Paragraph("Milestone 1", table_cell_style),
            Paragraph("Multi-Region VPC & Terraform Infrastructure as Code", table_cell_style),
            Paragraph("March 31, 2024", table_cell_style),
            Paragraph("$25,000.00", table_cell_style)
        ],
        [
            Paragraph("Milestone 2", table_cell_style),
            Paragraph("Kubernetes Cluster & GitOps CI/CD Automation", table_cell_style),
            Paragraph("May 15, 2024", table_cell_style),
            Paragraph("$35,000.00", table_cell_style)
        ],
        [
            Paragraph("Milestone 3", table_cell_style),
            Paragraph("SOC-2 Compliance & Zero-Trust Security Hardening", table_cell_style),
            Paragraph("June 30, 2024", table_cell_style),
            Paragraph("$20,000.00", table_cell_style)
        ],
        [
            Paragraph("<b>TOTAL</b>", table_cell_style),
            Paragraph("<b>Full SOW Project Budget Cap</b>", table_cell_style),
            Paragraph("<b>All Deliverables</b>", table_cell_style),
            Paragraph("<b>$80,000.00</b>", table_cell_style)
        ]
    ]

    t = Table(table_data, colWidths=[70, 240, 95, 95])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("TERMS AND CONDITIONS", h2_style))
    story.append(Paragraph("1. Any work exceeding the approved milestone caps must be authorized through a formal written Change Order signed by Acme Corporation's VP of Engineering.", body_style))
    story.append(Paragraph("2. Invoicing is governed strictly by Section 2 (Net-30) of MSA-2024-ACME-CYBER.", body_style))

    doc.build(story)
    print(f"Generated: {filepath}")

def build_invoice_compliant():
    filepath = os.path.join(OUTPUT_DIR, "INV_2024_081_Compliant.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("COMMERCIAL TAX INVOICE", title_style))
    story.append(Paragraph("<b>Cyberdyne Systems Inc.</b> | 2049 Silicon Parkway, San Jose, CA 95134", body_style))
    story.append(Spacer(1, 8))

    meta_data = [
        [Paragraph("<b>Invoice Number:</b> INV-2024-081", body_style), Paragraph("<b>Issue Date:</b> March 31, 2024", body_style)],
        [Paragraph("<b>Client:</b> Acme Corporation", body_style), Paragraph("<b>Payment Due Date:</b> April 30, 2024 (Net-30)", body_style)],
        [Paragraph("<b>Governing Contract:</b> MSA-2024-ACME-CYBER", body_style), Paragraph("<b>Payment Terms:</b> Net 30 Calendar Days", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    items = [
        [
            Paragraph("Item / Description", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Rate (USD)", table_header_style),
            Paragraph("Amount (USD)", table_header_style)
        ],
        [
            Paragraph("Milestone 1: Multi-Region VPC & Terraform IaC (Per SOW-2024-01)", table_cell_style),
            Paragraph("1", table_cell_style),
            Paragraph("$25,000.00", table_cell_style),
            Paragraph("$25,000.00", table_cell_style)
        ],
        [
            Paragraph("Subtotal", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("$25,000.00", table_cell_style)
        ],
        [
            Paragraph("State Sales Tax (8.25%)", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("$2,062.50", table_cell_style)
        ],
        [
            Paragraph("<b>TOTAL AMOUNT DUE</b>", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("<b>$27,062.50</b>", table_cell_style)
        ]
    ]

    t = Table(items, colWidths=[270, 40, 90, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e0f2fe')),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("REMITTANCE & WIRE INSTRUCTIONS", h2_style))
    story.append(Paragraph("Bank: Silicon Valley Corporate Bank | Routing Number: 121000358 | Account Number: 9876543210<br/>Per MSA § 2.3, interest of 1.5% per month applies only to undisputed balances overdue after April 30, 2024.", body_style))

    doc.build(story)
    print(f"Generated: {filepath}")

def build_invoice_disputed():
    filepath = os.path.join(OUTPUT_DIR, "INV_2024_099_Disputed.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("COMMERCIAL TAX INVOICE (AUDIT DISPUTED)", title_style))
    story.append(Paragraph("<b>Cyberdyne Systems Inc.</b> | 2049 Silicon Parkway, San Jose, CA 95134", body_style))
    story.append(Spacer(1, 8))

    meta_data = [
        [Paragraph("<b>Invoice Number:</b> INV-2024-099", body_style), Paragraph("<b>Issue Date:</b> May 15, 2024", body_style)],
        [Paragraph("<b>Client:</b> Acme Corporation", body_style), Paragraph("<b>Payment Due Date:</b> May 22, 2024 <i>[DISCREPANCY: Net-7]</i>", body_style)],
        [Paragraph("<b>Governing Contract:</b> MSA-2024-ACME-CYBER", body_style), Paragraph("<b>Payment Terms:</b> Net 7 Days Due Immediately", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    items = [
        [
            Paragraph("Item / Description", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Rate (USD)", table_header_style),
            Paragraph("Amount (USD)", table_header_style)
        ],
        [
            Paragraph("Milestone 2: Kubernetes Cluster & GitOps (Billed $55,000 vs SOW Cap of $35,000)", table_cell_style),
            Paragraph("1", table_cell_style),
            Paragraph("$55,000.00", table_cell_style),
            Paragraph("$55,000.00", table_cell_style)
        ],
        [
            Paragraph("Subtotal", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("$55,000.00", table_cell_style)
        ],
        [
            Paragraph("State Sales Tax (8.25%)", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("$4,537.50", table_cell_style)
        ],
        [
            Paragraph("<b>Late Payment Expedited Surcharge (15.0% Policy)</b>", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("<b>$8,250.00</b>", table_cell_style)
        ],
        [
            Paragraph("<b>TOTAL AMOUNT CLAIMED</b>", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph("<b>$67,787.50</b>", table_cell_style)
        ]
    ]

    t = Table(items, colWidths=[270, 40, 90, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#b91c1c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fee2e2')),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("AUDIT NOTICE & DISPUTE NOTES", h2_style))
    story.append(Paragraph("<b>DISPUTE SUMMARY:</b><br/>"
                           "1. <b>Late Fee Breach:</b> This invoice demands a 15.0% late penalty surcharge ($8,250.00), directly violating MSA Section 2.3 which caps monthly late penalties at 1.5%.<br/>"
                           "2. <b>Milestone Budget Overcharge:</b> Billed amount of $55,000.00 exceeds the SOW Milestone 2 fixed cap of $35,000.00 by $20,000.00 without an executed Change Order.<br/>"
                           "3. <b>Term Violation:</b> Demands Net-7 payment instead of contractually agreed Net-30 payment terms.", body_style))

    doc.build(story)
    print(f"Generated: {filepath}")

if __name__ == "__main__":
    build_msa()
    build_sow()
    build_invoice_compliant()
    build_invoice_disputed()
    print("All sample PDFs generated successfully in data/sample_documents/")
