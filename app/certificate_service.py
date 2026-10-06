from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen.canvas import Canvas


def generate_certificate(output_path: Path, recipient_name: str, course_name: str,
                         completion_date: str, event_name: str, issuer_name: str) -> None:
    # A single intentionally simple predefined template.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output_path), pagesize=landscape(letter))
    width, height = landscape(letter)
    canvas.setStrokeColor(HexColor("#1F4E79"))
    canvas.setLineWidth(5)
    canvas.rect(28, 28, width - 56, height - 56)
    canvas.setFillColor(HexColor("#1F4E79"))
    canvas.setFont("Helvetica-Bold", 30)
    canvas.drawCentredString(width / 2, height - 125, "CERTIFICATE OF COMPLETION")
    canvas.setFillColor(HexColor("#333333"))
    canvas.setFont("Helvetica", 15)
    canvas.drawCentredString(width / 2, height - 175, "This certificate is proudly presented to")
    canvas.setFillColor(HexColor("#B8860B"))
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawCentredString(width / 2, height - 225, recipient_name)
    canvas.setFillColor(HexColor("#333333"))
    canvas.setFont("Helvetica", 15)
    canvas.drawCentredString(width / 2, height - 270, f"for successfully completing {course_name}")
    canvas.setFont("Helvetica", 12)
    canvas.drawCentredString(width / 2, height - 305, f"Event: {event_name}   |   Date: {completion_date}")
    canvas.line(160, 105, 310, 105)
    canvas.line(width - 310, 105, width - 160, 105)
    canvas.setFont("Helvetica", 11)
    canvas.drawCentredString(235, 85, issuer_name)
    canvas.drawCentredString(width - 235, 85, "Authorized Signature")
    canvas.save()
