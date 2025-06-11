from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def gerar_pdf_chat(messages, titulo="Histórico de Estudo"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Chat", fontSize=12, leading=16, spaceAfter=12))

    story = [Paragraph(f"<b>{titulo}</b>", styles["Title"]), Spacer(1, 12)]

    for msg in messages:
        autor = "Você" if msg.type == "user" else "VestibulandoBot"
        texto = f"<b>{autor}:</b> {msg.content}"
        story.append(Paragraph(texto, styles["Chat"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
