import os
from pathlib import Path
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to add headers and 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Suppress header/footer on cover page if page 1
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 11 * inch - 36, "Acute Support — Executive Management & Cost Analysis Report")
            self.setStrokeColor(colors.HexColor("#D9D9D9"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            self.drawString(54, 36, "CONFIDENTIAL — FOR INTERNAL MANAGEMENT USE ONLY")
            self.line(54, 48, 8.5 * inch - 54, 48)
        else:
            # Footer on cover page
            page_text = f"Page 1 of {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            self.drawString(54, 36, "Acute Support Transformation Strategy | August 2026")
            self.setStrokeColor(colors.HexColor("#D9D9D9"))
            self.setLineWidth(0.5)
            self.line(54, 48, 8.5 * inch - 54, 48)
            
        self.restoreState()

def build_pdf_report(output_pdf_path):
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1F4E79'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#4A607A'),
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1F4E79'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2E75B6'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#262626'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    tbl_header_style = ParagraphStyle(
        'TblHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#262626')
    )

    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=tbl_cell_style,
        alignment=1
    )

    tbl_cell_right = ParagraphStyle(
        'TblCellRight',
        parent=tbl_cell_style,
        alignment=2
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1F4E79')
    )

    story = []

    # Title Banner
    story.append(Paragraph("Executive Management & Financial Cost Analysis", title_style))
    story.append(Paragraph("Acute Support Case Trends, Support Analyst Effort & Automation Savings Potential", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1F4E79'), spaceAfter=15))

    # Metadata Table
    meta_data = [
        [Paragraph("<b>Author:</b> Lee Booth", body_style), Paragraph("<b>Date:</b> August 2026", body_style)],
        [Paragraph("<b>Scope:</b> Meds & Symphony Support Suites (7 Trend Files)", body_style), Paragraph("<b>Target Audience:</b> Senior Operations & Transformation Leadership", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[240, 244])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F2F4F8')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This management report presents a rigorous, evidence-based evaluation of operational ticket demand across the <b>Meds</b> and <b>Symphony</b> support suites, analyzing <b>724 cases</b> spanning 5 core technical trends (Robot, Merge, Lock, Audit, DAD) over a 12-month period. The analysis couples ServiceNow SLA tracking with financial modeling of analyst labor costs based on an average Support Analyst base salary of <b>£28,000/annum</b> to quantify baseline operational expenditure and identify actionable cost reduction opportunities.",
        body_style
    ))

    # Key Highlights Box
    exec_box_data = [[
        Paragraph(
            "<b>Key Financial & Operational Findings (Based on £28,000 Base Salary):</b><br/>"
            "• <b>Total Volume & Effort:</b> 724 cases consume approximately <b>844 hours</b> of direct analyst touch-time annually.<br/>"
            "• <b>Baseline Labor Spend:</b> At an average base salary of <b>£28,000/annum</b> (plus 25% employer on-costs = £35,000 TCOE; £21.88/hr), direct labor expenditure on these 5 trends is <b>£18,462.50 annually</b>.<br/>"
            "• <b>Targeted Savings Potential:</b> Implementing targeted interventions (RPA automation, self-service tools, and triage KB articles) can eliminate <b>~70.7%</b> of manual handling.<br/>"
            "• <b>Net Business Impact:</b> <b>£13,050.76 in annual financial savings</b> and <b>596.5 analyst hours freed</b> for higher-value transformation engineering.",
            callout_style
        )
    ]]
    exec_box_table = Table(exec_box_data, colWidths=[484])
    exec_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF3F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2E75B6')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(exec_box_table)
    story.append(Spacer(1, 15))

    # 2. Product & Trend Volume Analysis
    story.append(Paragraph("2. Product & Trend Dataset Breakdown (7 Worksheets)", h1_style))
    story.append(Paragraph(
        "The underlying dataset comprises 7 distinct datasets: 2 product-level combined sheets (Meds Combined and Symphony Combined) and 5 granular trend worksheets. The table below details ticket volume, SLA tracking coverage, resolution rates, and resolution speed.",
        body_style
    ))

    # Table 1: Volume & SLA Summary
    t1_headers = [
        Paragraph("<b>Product Suite</b>", tbl_header_style),
        Paragraph("<b>Trend Worksheet</b>", tbl_header_style),
        Paragraph("<b>Total Cases</b>", tbl_header_style),
        Paragraph("<b>SLA Matched</b>", tbl_header_style),
        Paragraph("<b>Resolved Cases</b>", tbl_header_style),
        Paragraph("<b>Median TTR</b>", tbl_header_style),
        Paragraph("<b>Median SLA Business</b>", tbl_header_style)
    ]
    
    t1_rows = [
        [Paragraph("Meds", tbl_cell_style), Paragraph("Meds Combined", tbl_cell_style), Paragraph("454", tbl_cell_center), Paragraph("398 (87.7%)", tbl_cell_center), Paragraph("445 (98.0%)", tbl_cell_center), Paragraph("4h 22m", tbl_cell_center), Paragraph("2h 55m", tbl_cell_center)],
        [Paragraph("Meds", tbl_cell_style), Paragraph("Robot", tbl_cell_style), Paragraph("156", tbl_cell_style), Paragraph("140 (89.7%)", tbl_cell_center), Paragraph("153 (98.1%)", tbl_cell_center), Paragraph("1h 51m", tbl_cell_center), Paragraph("1h 50m", tbl_cell_center)],
        [Paragraph("Meds", tbl_cell_style), Paragraph("Merge", tbl_cell_style), Paragraph("132", tbl_cell_style), Paragraph("124 (93.9%)", tbl_cell_center), Paragraph("127 (96.2%)", tbl_cell_center), Paragraph("1d 22h 45m", tbl_cell_center), Paragraph("6h 20m", tbl_cell_center)],
        [Paragraph("Meds", tbl_cell_style), Paragraph("Lock", tbl_cell_style), Paragraph("166", tbl_cell_style), Paragraph("134 (80.7%)", tbl_cell_center), Paragraph("165 (99.4%)", tbl_cell_center), Paragraph("3h 35m", tbl_cell_center), Paragraph("2h 31m", tbl_cell_center)],
        [Paragraph("Symphony", tbl_cell_style), Paragraph("Symphony Combined", tbl_cell_style), Paragraph("270", tbl_cell_style), Paragraph("234 (86.7%)", tbl_cell_center), Paragraph("267 (98.9%)", tbl_cell_center), Paragraph("20h 31m", tbl_cell_center), Paragraph("3h 44m", tbl_cell_center)],
        [Paragraph("Symphony", tbl_cell_style), Paragraph("Audit", tbl_cell_style), Paragraph("122", tbl_cell_style), Paragraph("109 (89.3%)", tbl_cell_center), Paragraph("120 (98.4%)", tbl_cell_center), Paragraph("1d 21h 10m", tbl_cell_center), Paragraph("7h 35m", tbl_cell_center)],
        [Paragraph("Symphony", tbl_cell_style), Paragraph("DAD", tbl_cell_style), Paragraph("148", tbl_cell_style), Paragraph("125 (84.5%)", tbl_cell_center), Paragraph("147 (99.3%)", tbl_cell_center), Paragraph("3h 31m", tbl_cell_center), Paragraph("1h 33m", tbl_cell_center)],
        [Paragraph("<b>TOTAL</b>", tbl_cell_style), Paragraph("<b>All Trends (724)</b>", tbl_cell_style), Paragraph("<b>724</b>", tbl_cell_center), Paragraph("<b>632 (87.3%)</b>", tbl_cell_center), Paragraph("<b>712 (98.3%)</b>", tbl_cell_center), Paragraph("<b>--</b>", tbl_cell_center), Paragraph("<b>--</b>", tbl_cell_center)]
    ]

    t1_table = Table([t1_headers] + t1_rows, colWidths=[60, 95, 55, 75, 75, 62, 62])
    t1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E79')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F2F4F8')),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#F2F4F8')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF3F9')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t1_table)
    story.append(Spacer(1, 15))

    # 3. Financial Model & Analyst Costings
    story.append(Paragraph("3. Financial Model & Support Analyst Costings", h1_style))
    story.append(Paragraph(
        "To establish direct support expenditure, analyst compensation is converted into an effective hourly rate based on an average Support Analyst salary of £28,000. Active handling time ('touch time') is modeled per case type to isolate true labor effort from passive ServiceNow ticket queue elapsed time (TTR).",
        body_style
    ))

    # Financial Assumptions Box
    story.append(Paragraph("<b>Baseline Financial Parameters (£28k Salary Basis):</b>", h2_style))
    story.append(Paragraph("• <b>Support Analyst Base Salary:</b> £28,000 / year", bullet_style))
    story.append(Paragraph("• <b>Employer On-Costs (NI, Pension, Overheads @ 25%):</b> £7,000 / year", bullet_style))
    story.append(Paragraph("• <b>Total Cost of Employment (TCOE):</b> £35,000 / year", bullet_style))
    story.append(Paragraph("• <b>Effective Annual Productive Hours:</b> 1,600 hours (37.5 hrs/wk less leave, training & admin)", bullet_style))
    story.append(Paragraph("• <b>Fully Loaded Analyst Hourly Rate:</b> <b>£21.875 / hour</b> (£35,000 / 1,600 hrs)", bullet_style))
    story.append(Spacer(1, 10))

    # Table 2: Trend Costing & Savings Breakdown
    t2_headers = [
        Paragraph("<b>Trend Category</b>", tbl_header_style),
        Paragraph("<b>Cases</b>", tbl_header_style),
        Paragraph("<b>Avg Touch Time</b>", tbl_header_style),
        Paragraph("<b>Total Labor Hours</b>", tbl_header_style),
        Paragraph("<b>Baseline Labor Cost</b>", tbl_header_style),
        Paragraph("<b>Target Savings %</b>", tbl_header_style),
        Paragraph("<b>Hours Saved</b>", tbl_header_style),
        Paragraph("<b>Annual Savings (£)</b>", tbl_header_style)
    ]

    t2_rows = [
        [Paragraph("<b>Robot</b> (Meds)", tbl_cell_style), Paragraph("156", tbl_cell_center), Paragraph("0.75 hrs (45m)", tbl_cell_center), Paragraph("117.0 hrs", tbl_cell_right), Paragraph("£2,559.38", tbl_cell_right), Paragraph("80.0%", tbl_cell_center), Paragraph("93.6 hrs", tbl_cell_right), Paragraph("<b>£2,047.50</b>", tbl_cell_right)],
        [Paragraph("<b>Merge</b> (Meds)", tbl_cell_style), Paragraph("132", tbl_cell_center), Paragraph("2.50 hrs (150m)", tbl_cell_center), Paragraph("330.0 hrs", tbl_cell_right), Paragraph("£7,218.75", tbl_cell_right), Paragraph("50.0%", tbl_cell_center), Paragraph("165.0 hrs", tbl_cell_right), Paragraph("<b>£3,609.38</b>", tbl_cell_right)],
        [Paragraph("<b>Lock</b> (Meds)", tbl_cell_style), Paragraph("166", tbl_cell_center), Paragraph("0.50 hrs (30m)", tbl_cell_center), Paragraph("83.0 hrs", tbl_cell_right), Paragraph("£1,815.63", tbl_cell_right), Paragraph("90.0%", tbl_cell_center), Paragraph("74.7 hrs", tbl_cell_right), Paragraph("<b>£1,634.06</b>", tbl_cell_right)],
        [Paragraph("<b>Audit</b> (Symphony)", tbl_cell_style), Paragraph("122", tbl_cell_center), Paragraph("1.50 hrs (90m)", tbl_cell_center), Paragraph("183.0 hrs", tbl_cell_right), Paragraph("£4,003.13", tbl_cell_right), Paragraph("75.0%", tbl_cell_center), Paragraph("137.3 hrs", tbl_cell_right), Paragraph("<b>£3,002.34</b>", tbl_cell_right)],
        [Paragraph("<b>DAD</b> (Symphony)", tbl_cell_style), Paragraph("148", tbl_cell_center), Paragraph("0.75 hrs (45m)", tbl_cell_center), Paragraph("111.0 hrs", tbl_cell_right), Paragraph("£2,428.13", tbl_cell_right), Paragraph("60.0%", tbl_cell_center), Paragraph("66.6 hrs", tbl_cell_right), Paragraph("<b>£1,456.88</b>", tbl_cell_right)],
        [Paragraph("<b>TOTAL / OVERALL</b>", tbl_cell_style), Paragraph("<b>724</b>", tbl_cell_center), Paragraph("<b>1.17 hrs avg</b>", tbl_cell_center), Paragraph("<b>844.0 hrs</b>", tbl_cell_right), Paragraph("<b>£18,462.50</b>", tbl_cell_right), Paragraph("<b>70.7%</b>", tbl_cell_center), Paragraph("<b>596.5 hrs</b>", tbl_cell_right), Paragraph("<b>£13,050.76</b>", tbl_cell_right)]
    ]

    t2_table = Table([t2_headers] + t2_rows, colWidths=[95, 40, 65, 55, 62, 52, 55, 60])
    t2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E79')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F9FAFC')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF3F9')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t2_table)
    story.append(Spacer(1, 15))

    # 4. Strategic Action Plan & Business Case
    story.append(Paragraph("4. Strategic Action Plan & Target Interventions", h1_style))
    story.append(Paragraph(
        "To capture the identified <b>£13,050.76 annual savings</b> and eliminate <b>596.5 hours of routine manual effort</b>, a prioritized transformation roadmap is recommended:",
        body_style
    ))

    story.append(Paragraph("<b>Priority 1 — Lock & Robot Automation (Immediate ROI)</b>", h2_style))
    story.append(Paragraph("• <b>Meds Lock Cases (166 cases / £1.82k cost):</b> Implement an automated DB session unlock daemon or user self-service portal. Target reduction: 90% (£1.63k annual savings, 74.7 hrs freed).", bullet_style))
    story.append(Paragraph("• <b>Meds Robot Cases (156 cases / £2.56k cost):</b> Deploy RPA scripts for automated picking ticket printing error resolution. Target reduction: 80% (£2.05k annual savings, 93.6 hrs freed).", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Priority 2 — Symphony Audit Portal & DAD Auto-Diagnostics</b>", h2_style))
    story.append(Paragraph("• <b>Symphony Audit Cases (122 cases / £4.00k cost):</b> Build a self-service compliance audit report extractor. Target reduction: 75% (£3.00k annual savings, 137.3 hrs freed).", bullet_style))
    story.append(Paragraph("• <b>Symphony DAD Cases (148 cases / £2.43k cost):</b> Implement automated diagnostic tools and triage rules for digital asset errors. Target reduction: 60% (£1.46k annual savings, 66.6 hrs freed).", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Priority 3 — Meds Patient Merge Triage & Wizard</b>", h2_style))
    story.append(Paragraph("• <b>Meds Merge Cases (132 cases / £7.22k cost):</b> Patient record merges represent the highest single labor drain (330 total hours). Develop a guided validation wizard and automated pre-check script to reduce touch time by 50% (£3.61k annual savings, 165.0 hrs freed).", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report at: {output_pdf_path}")

if __name__ == "__main__":
    out_pdf = Path("/home/lee/Documents/1 Projects/AcuteSupport/outputs/AcuteSupport_Executive_Financial_Report.pdf")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    build_pdf_report(out_pdf)
