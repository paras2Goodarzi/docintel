from pathlib import Path

from app.services.text_cleaner import clean_text

src = Path("data/processed/B_gray_big_psm11.txt")
dst = Path("data/processed/B_gray_big_psm11_clean.txt")

raw = src.read_text(encoding="utf-8")
cleaned = clean_text(raw)
dst.write_text(cleaned, encoding="utf-8")

print(f"raw: {len(raw)} chars, {len(raw.splitlines())} lines")
print(f"clean: {len(cleaned)} chars, {len(cleaned.splitlines())} lines")