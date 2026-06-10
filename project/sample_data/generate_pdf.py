import os
import json
import html
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
        # Page 1 is the cover page
        if self._pageNumber == 1:
            self.saveState()
            # Left vertical indigo accent line
            self.setFillColor(colors.HexColor("#4f46e5"))
            self.rect(0, 0, 18, 792, fill=True, stroke=False)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (Running Title)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 738, 558, 738)
        self.drawString(54, 745, "Helpdesk Ticket System — Sample Data Report")
        
        # Footer
        self.line(54, 54, 558, 54)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential — Test Case Reference & Evaluation Assets")
        self.restoreState()

def escape_html(text):
    escaped = html.escape(text)
    lines = escaped.split("\n")
    formatted_lines = []
    for line in lines:
        # Convert only leading spaces to &nbsp; to preserve code/JSON indentation
        leading_spaces_count = len(line) - len(line.lstrip(' '))
        formatted_line = "&nbsp;" * leading_spaces_count + line[leading_spaces_count:]
        # Convert multiple spaces (2 or more) to &nbsp; to maintain formatting
        while "  " in formatted_line:
            formatted_line = formatted_line.replace("  ", "&nbsp;&nbsp;")
        formatted_lines.append(formatted_line)
    return "<br/>".join(formatted_lines)

def build_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "helpdesk_sample_data.pdf")
    
    # Read files
    try:
        with open(os.path.join(script_dir, "input_issue_1.txt"), "r", encoding="utf-8") as f:
            input_1 = f.read().strip()
        with open(os.path.join(script_dir, "expected_output_1.json"), "r", encoding="utf-8") as f:
            output_1 = f.read().strip()
        with open(os.path.join(script_dir, "input_issue_2.txt"), "r", encoding="utf-8") as f:
            input_2 = f.read().strip()
        with open(os.path.join(script_dir, "expected_output_2.json"), "r", encoding="utf-8") as f:
            output_2 = f.read().strip()
    except Exception as e:
        print(f"Error reading sample files: {e}")
        return

    # Document setup
    # Margins: 0.75 in (54 pt) left/right, 1.0 in (72 pt) top/bottom
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    # Style definitions
    styles = getSampleStyleSheet()
    Normal = styles['Normal']
    
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=Normal,
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=Normal,
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=Normal,
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    
    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=Normal,
        fontName='Courier',
        fontSize=8.0,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )
    
    code_title_style = ParagraphStyle(
        'CodeTitle',
        parent=Normal,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        spaceAfter=4
    )

    terminal_code_style = ParagraphStyle(
        'TerminalCode',
        parent=code_style,
        textColor=colors.HexColor("#f1f5f9")
    )
    
    terminal_title_style = ParagraphStyle(
        'TerminalTitle',
        parent=code_title_style,
        textColor=colors.HexColor("#94a3b8")
    )

    story = []
    
    # ------------------ PAGE 1: COVER PAGE ------------------
    story.append(Spacer(1, 120))
    story.append(Paragraph("Helpdesk Ticket<br/>Management System", cover_title_style))
    story.append(Paragraph("Autonomous AI Agent & Gemini Classification Verification", cover_subtitle_style))
    
    # Colored accent separator line
    sep_table = Table([[""]], colWidths=[480], rowHeights=[4])
    sep_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#4f46e5")),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sep_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(
        "This document contains representative test cases and seeded data "
        "designed to validate the system's duplicate ticket mitigation logic, "
        "priority assessment, and automated classification routing workflows.",
        body_style
    ))
    story.append(Spacer(1, 80))
    
    # Metadata Block
    metadata_data = [
        [Paragraph("Document Type", table_cell_bold_style), Paragraph("Sample Data & Verification Guide", table_cell_style)],
        [Paragraph("Target Component", table_cell_bold_style), Paragraph("AI Classification and Duplicate Check Pipeline", table_cell_style)],
        [Paragraph("Evaluation Framework", table_cell_bold_style), Paragraph("FastAPI REST & FastMCP stdio Protocols", table_cell_style)],
        [Paragraph("Generation Date", table_cell_bold_style), Paragraph("June 10, 2026", table_cell_style)],
    ]
    metadata_table = Table(metadata_data, colWidths=[130, 350])
    metadata_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(metadata_table)
    
    story.append(PageBreak())
    
    # ------------------ PAGE 2: DETAILS ------------------
    story.append(Paragraph("1. Purpose & Directory Structure", h1_style))
    story.append(Paragraph(
        "The `sample_data/` directory houses inputs and outputs for regression testing. "
        "These test cases feed directly into standard testing suites (e.g., `test_agent.py`) "
        "to guarantee that issue classification and similarity matching logic remain consistent "
        "across core upgrades.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Directory Structure Table
    struct_headers = [Paragraph("File Path", table_header_style), Paragraph("Description", table_header_style)]
    struct_data = [
        struct_headers,
        [Paragraph("sample_data/README.md", table_cell_bold_style), Paragraph("Documentation of test scenarios and commands", table_cell_style)],
        [Paragraph("sample_data/input_issue_1.txt", table_cell_bold_style), Paragraph("Raw ticket text for Case 1 (payments down)", table_cell_style)],
        [Paragraph("sample_data/expected_output_1.json", table_cell_bold_style), Paragraph("Expected classification properties for Case 1", table_cell_style)],
        [Paragraph("sample_data/input_issue_2.txt", table_cell_bold_style), Paragraph("Raw ticket text for Case 2 (slow queries)", table_cell_style)],
        [Paragraph("sample_data/expected_output_2.json", table_cell_bold_style), Paragraph("Expected comment action properties for Case 2", table_cell_style)],
    ]
    struct_table = Table(struct_data, colWidths=[180, 324])
    struct_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(struct_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("2. Test Cases Specification", h1_style))
    
    # Test Case Helper function
    def create_case_flowables(case_title, case_desc, input_filename, input_text, output_filename, output_text):
        case_story = []
        case_story.append(Paragraph(case_title, h2_style))
        case_story.append(Paragraph(case_desc, body_style))
        
        # Make Code Boxes
        def make_code_box(filename, content):
            box_content = [
                Paragraph(filename, code_title_style),
                Paragraph(escape_html(content), code_style)
            ]
            t = Table([[box_content]], colWidths=[246])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            return t
        
        input_box = make_code_box(input_filename, input_text)
        output_box = make_code_box(output_filename, output_text)
        
        # Side by side table
        grid_table = Table([[input_box, "", output_box]], colWidths=[246, 12, 246])
        grid_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        case_story.append(grid_table)
        case_story.append(Spacer(1, 15))
        return KeepTogether(case_story)

    # Add Case 1
    story.append(create_case_flowables(
        "Case 1: Critical Payment System Outage (New Ticket)",
        "A severe issue indicating business-critical systems are offline. "
        "Since no duplicate ticket exists in the database, the ReAct loop "
        "automatically classifies this as CRITICAL urgency under the 'Payments' "
        "category and creates a new ticket.",
        "input_issue_1.txt",
        input_1,
        "expected_output_1.json",
        output_1
    ))
    
    # Add Case 2
    story.append(create_case_flowables(
        "Case 2: Query Timeout Warning (Duplicate Verification)",
        "An issue describing query latency overlaps with active tickets in the seeded "
        "database. Jaccard similarity token checking triggers duplicate mitigation (>= 25% threshold), "
        "routing the agent to append a comment to the existing ticket rather than duplicating it.",
        "input_issue_2.txt",
        input_2,
        "expected_output_2.json",
        output_2
    ))
    
    story.append(PageBreak())
    
    # ------------------ PAGE 3: USAGE IN TESTING ------------------
    story.append(Paragraph("3. Verification & Execution Instructions", h1_style))
    story.append(Paragraph(
        "The classification parsing engine and ReAct workspace triggers are tested "
        "systematically by reading these files in isolated runner environments. Use the following "
        "commands to execute tests locally or inspect agent classification fallbacks.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Commands Code Box
    cmd_text = (
        "# 1. Run the test agent runner framework\n"
        "python project/agent/test_agent.py\n\n"
        "# 2. Run the Gemini mock and API classifier test suite\n"
        "python project/agent/test_gemini_classifier.py"
    )
    
    cmd_box_content = [
        Paragraph("Command Console", terminal_title_style),
        Paragraph(escape_html(cmd_text), terminal_code_style)
    ]
    
    cmd_box = Table([[ cmd_box_content ]], colWidths=[504])
    cmd_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(cmd_box)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(
        "The automated classification will leverage your configured `GEMINI_API_KEY` "
        "in your local `.env` environment. If the API key is not present or rate-limits "
        "are hit, the workflow falls back gracefully to local rule-based parsing.",
        body_style
    ))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at {pdf_path}")

if __name__ == "__main__":
    build_pdf()
