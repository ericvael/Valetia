from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from valetia.utils.markdown_sanitizer import markdown_to_safe_html
from tempfile import NamedTemporaryFile
import weasyprint

router = APIRouter()

@router.post("/rapport/generer", summary="Génère un rapport PDF à partir de contenu Markdown")
def generer_rapport(markdown: str = Body(..., embed=True)):
    html_content = markdown_to_safe_html(markdown)
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            h1, h2, h3 {{ color: #004080; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    tmp = NamedTemporaryFile(delete=False, suffix=".pdf")
    weasyprint.HTML(string=full_html).write_pdf(tmp.name)

    return FileResponse(tmp.name, media_type='application/pdf', filename="rapport_valetia.pdf")
