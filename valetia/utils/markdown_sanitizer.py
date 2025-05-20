import markdown2
import bleach

def markdown_to_safe_html(markdown_text: str) -> str:
    raw_html = markdown2.markdown(markdown_text)

    allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS).union({
        "p", "pre", "table", "thead", "tbody", "tr", "td", "th", "code"
    })
    allowed_attrs = {
        "*": ["class", "style", "align"],
        "a": ["href", "title", "target"],
    }

    clean_html = bleach.clean(
        raw_html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

    return clean_html
