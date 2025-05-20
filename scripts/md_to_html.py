#!/usr/bin/env python3
"""
Convertisseur Markdown (.md) vers HTML sécurisé (.html)
Utilise markdown2 + bleach (nettoyage HTML)
Usage :
    python scripts/md_to_html.py fichier.md
"""

import sys
import os
from valetia.utils.markdown_sanitizer import markdown_to_safe_html

def main():
    if len(sys.argv) < 2:
        print("Usage : python scripts/md_to_html.py fichier.md")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"Erreur : le fichier {input_path} n'existe pas.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    html = markdown_to_safe_html(markdown_text)

    output_path = input_path.rsplit(".", 1)[0] + ".html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Fichier HTML généré : {output_path}")

if __name__ == "__main__":
    main()
