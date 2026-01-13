from weasyprint import HTML, CSS
import tempfile
import requests

def gerar_pdf_weasy(url):
    html = HTML(url)
    pdf_bytes = html.write_pdf()
    return pdf_bytes