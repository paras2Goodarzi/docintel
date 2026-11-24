import os
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = str(Path("tessdata").resolve())

IMAGE_PATH = Path("data/raw/sample1.png")
OUT_DIR = Path("data/processed")


def make_gray(img: Image.Image) -> Image.Image:
    """تبدیل تصویر رنگی به سطوح خاکستری."""
    return ImageOps.grayscale(img)


def upscale(img: Image.Image, factor: int = 2) -> Image.Image:
    """بزرگ‌کردن تصویر به اندازه factor برابر."""
    new_size = (img.width * factor, img.height * factor)
    return img.resize(new_size, Image.Resampling.LANCZOS)


def binarize(img: Image.Image, threshold: int = 160) -> Image.Image:
    """هر پیکسل روشن‌تر از threshold سفید و بقیه سیاه."""
    return img.point(lambda p: 255 if p > threshold else 0)


def run_ocr(img: Image.Image, psm: int) -> str:
    return pytesseract.image_to_string(img, lang="fas+eng", config=f"--psm {psm}")


original = Image.open(IMAGE_PATH)
"""زنجیره پردازش از داخل به بیرون: اول خاکستری، بعد ۲ برابر، بعد افزایش کنتراست."""
gray_big = ImageOps.autocontrast(upscale(make_gray(original)))
binary = binarize(gray_big)
"""یه دیکشنری از سه نسخه تصویر: اصلی، خاکستری و بزرگ‌شده، و باینری‌شده. """
variants = {
    "A_original": original,
    "B_gray_big": gray_big,
    "C_binary": binary,
}
""" وشه خروجی رو می‌سازه و اگه از قبل بود خطا نمی‌ده. """
OUT_DIR.mkdir(parents=True, exist_ok=True)
""""حلقه آخر: برای هر نسخه تصویر، عکس پردازش‌شده رو ذخیره می‌کنه (تا با چشم ببینی)، بعد با psm ۳ و ۱۱ OCR می‌گیره و هر خروجی رو توی فایل جدا می‌نویسه. در نهایت ۶ فایل متنی و ۳ فایل عکس می‌سازه."""
for name, img in variants.items():
    img.save(OUT_DIR / f"{name}.png")
    for psm in (3, 11):
        text = run_ocr(img, psm)
        out_file = OUT_DIR / f"{name}_psm{psm}.txt"
        out_file.write_text(text, encoding="utf-8")
        print(f"{name} psm={psm}: {len(text)} chars -> {out_file}")