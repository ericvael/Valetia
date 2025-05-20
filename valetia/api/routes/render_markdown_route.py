from fastapi import APIRouter, Query
from valetia.utils.markdown_sanitizer import markdown_to_safe_html

router = APIRouter()

@router.get("/render_markdown", summary="Convertir du markdown en HTML sécurisé")
def render_markdown(text: str = Query(..., description="Texte Markdown à convertir")):
    html = markdown_to_safe_html(text)
    return {"html": html}

