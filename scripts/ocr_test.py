import os
from pathlib import Path

import pytesseract
from PIL import Image

# ۱) آدرس برنامه Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ۲) به Tesseract می‌گیم فایل‌های زبان کجاست (پوشه tessdata داخل پروژه)
os.environ["TESSDATA_PREFIX"] = str(Path("tessdata").resolve())

# ۳) مسیر ورودی و خروجی
image_path = Path("data/raw/sample1.png")
output_path = Path("data/processed/sample1.txt")

# ۴) باز کردن عکس
image = Image.open(image_path)

# ۵) اجرای OCR
text = pytesseract.image_to_string(image, lang="fas+eng")

# ۶) ذخیره خروجی
output_path.write_text(text, encoding="utf-8")
print(f"OCR done. {len(text)} characters saved to {output_path}")