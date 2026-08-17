"""Simple helper to convert docs/REFLECTION.md to docs/REFLECTION.pdf.

This script uses reportlab if installed. If not available it will print an
instruction so you can run the conversion locally (pip install reportlab).
"""
from pathlib import Path


def md_to_text(md: str) -> str:
    # Very small markdown-to-text fallback: strip headings and keep lines
    lines = []
    for line in md.splitlines():
        if line.startswith("#"):
            lines.append(line.lstrip("# "))
        else:
            lines.append(line)
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    md_path = root / "docs" / "REFLECTION.md"
    pdf_path = root / "docs" / "REFLECTION.pdf"
    if not md_path.exists():
        print("docs/REFLECTION.md not found.")
        return

    text = md_to_text(md_path.read_text(encoding="utf-8"))

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter
        margin = 72
        y = height - margin
        for line in text.splitlines():
            if y < margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line[:200])
            y -= 12
        c.save()
        print(f"Wrote {pdf_path}")
    except Exception:
        print("reportlab not installed. To create a PDF locally: pip install reportlab && python tools/convert_reflection_to_pdf.py")


if __name__ == "__main__":
    main()
