from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm

def gerar_pdf(conteudo, titulo="Conteúdo Exportado"):
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
    styles.add(ParagraphStyle(name="Body", fontSize=12, leading=16, spaceAfter=12))

    story = []

    # Título
    story.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Conteúdo com formatação
    for linha in conteudo.strip().split("\n"):
        story.append(Paragraph(linha.strip(), styles["Body"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
