from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def add_watermark_to_pdf_memory(input_pdf, output_pdf, watermark_text):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for page_num, page in enumerate(reader.pages):
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        c.setFont("Times-Roman", 120)
        c.setFillColorRGB(0.5, 0.5, 0.5, 0.2)
        
        c.saveState()
        c.translate(page_width/2, page_height/2)
        c.rotate(45)
        
        text_width = c.stringWidth(watermark_text, "Times-Roman", 120)
        c.drawString(-text_width/2, -60, watermark_text)
        
        c.restoreState()
        c.save()
        
        packet.seek(0)
        
        watermark_pdf = PdfReader(packet)
        watermark_page = watermark_pdf.pages[0]
        
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    with open(output_pdf, "wb") as f:
        writer.write(f)
    
if __name__ == "__main__":
    add_watermark_to_pdf_memory("Icarus.pdf", "Icarus_watermarked.pdf", "Cherry")