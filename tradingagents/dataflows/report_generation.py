from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import markdown

def generate_report(symbol_to_analysis: defaultdict(list)):
    '''It is a very simple example.

    Key is symbol, value is list[str]. Image is from ./imgs/{symbol}_candle.png.
    Example usage:
    generate_report({symbol: [transcript_response, candle_response, llm_response]})
    '''
    # Create the document
    pdf_path=f'./reports/analysis_{'_'.join(symbol_to_analysis.keys())}.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    for symbol, long_texts in symbol_to_analysis.items():
        title = Paragraph(symbol, styles['Title'])
        story.append(title)

        # Long wrapped text as a Paragraph
        for long_text in long_texts:
            para = Paragraph(markdown.markdown(long_text), styles['Normal'])
            story.append(para)

        # Spacer for some vertical gap between text and image
        story.append(Spacer(1, 0.2 * inch))

        # Add image (local path)

        img_path = f'./imgs/{symbol}_candle.png'
        img = Image(img_path)

        # Optionally scale image (keep aspect ratio)
        img.drawHeight = 6 * inch
        img.drawWidth = 8 * inch
        story.append(img)
        story.append(PageBreak())  # Start a new page
    # Build PDF
    doc.build(story)