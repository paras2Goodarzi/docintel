import os
from dataclasses import dataclass
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image, ImageOps

from app.services.text_cleaner import clean_text

# --- تنظیمات ---------------------------------------------------------------

# ریشه پروژه: app/services/ocr.py -> parents[0]=services, [1]=app, [2]=ریشه
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# آدرس tesseract.exe؛ با متغیر محیطی TESSERACT_CMD قابل تغییره (برای Docker لازم می‌شه)
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# پوشه فایل‌های زبان داخل پروژه
os.environ["TESSDATA_PREFIX"] = str(PROJECT_ROOT / "tessdata")

LANGS = "fas+eng"


# --- ساختار خروجی ----------------------------------------------------------

@dataclass
class PageResult:
    page_no: int  # شماره صفحه (از ۱)
    text: str     # متن تمیز‌شده


# --- پیش‌پردازش و OCR تصویر -----------------------------------------------

def preprocess(img: Image.Image, scale: int = 1) -> Image.Image:
    """خاکستری، بزرگ‌کردن (اختیاری) و افزایش کنتراست."""
    img = ImageOps.grayscale(img)
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
    return ImageOps.autocontrast(img)


def ocr_image(img: Image.Image, psm: int = 3, scale: int = 1) -> str:
    """OCR یک تصویر و برگرداندن متن تمیز‌شده."""
    prepared = preprocess(img, scale=scale)
    raw = pytesseract.image_to_string(prepared, lang=LANGS, config=f"--psm {psm}")
    return clean_text(raw)


# --- PDF -------------------------------------------------------------------

def ocr_pdf(pdf_path: Path, dpi: int = 300, psm: int = 3) -> list[PageResult]:
    """هر صفحه PDF را به تصویر تبدیل و OCR می‌کند."""
    results: list[PageResult] = []
    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            text = ocr_image(img, psm=psm, scale=1)
            results.append(PageResult(page_no=index, text=text))
    return results


# --- ورودی عمومی -----------------------------------------------------------

def ocr_file(path: Path) -> list[PageResult]:
    """بر اساس پسوند فایل، PDF یا تصویر را پردازش می‌کند."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return ocr_pdf(path)
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        with Image.open(path) as img:
            return [PageResult(page_no=1, text=ocr_image(img, scale=2))]
    raise ValueError(f"Unsupported file type: {suffix}")