import sys
from pathlib import Path

from app.services.ocr import ocr_file

if len(sys.argv) != 2:
    print("Usage: python -m scripts.pdf_demo <file>")
    sys.exit(1)

src = Path(sys.argv[1])
out_dir = Path("data/processed")
out_dir.mkdir(parents=True, exist_ok=True)

pages = ocr_file(src)

for page in pages:
    out_file = out_dir / f"{src.stem}_page{page.page_no}.txt"
    out_file.write_text(page.text, encoding="utf-8")
    print(f"page {page.page_no}: {len(page.text)} chars -> {out_file}")