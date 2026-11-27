# Persian Document Intelligence Platform

سرویسی برای استخراج متن از اسناد فارسی/انگلیسی (PDF و تصویر) و آماده‌سازی آن‌ها برای جستجوی معنایی، RAG و گراف دانش.

> **وضعیت پروژه:** فاز ۱ (OCR و API) تکمیل شده است. فاز ۲ (ذخیره‌سازی SQL) در حال پیاده‌سازی است.

## هدف

دریافت یک سند (PDF، عکس یا اسکن)، استخراج متن تمیز فارسی از آن و ارائه نتیجه از طریق API. فازهای بعدی روی همین پایه، جستجوی برداری، پرسش‌وپاسخ با LLM و گراف دانش را اضافه می‌کنند.

## فاز ۱: OCR و پایپ‌لاین اسناد

**جریان کار:** فایل ← تشخیص نوع (PDF/تصویر) ← تبدیل صفحه‌ها به تصویر ← پیش‌پردازش ← OCR ← پاک‌سازی متن ← پاسخ JSON

| بخش | توضیح | فایل |
|---|---|---|
| OCR | Tesseract با زبان `fas+eng`، پشتیبانی PDF چندصفحه‌ای (PyMuPDF با ۳۰۰ DPI) و تصویر | `app/services/ocr.py` |
| پیش‌پردازش | خاکستری‌سازی و افزایش کنتراست؛ در تصاویر کوچک بزرگ‌نمایی ۲ برابر | `app/services/ocr.py` |
| پاک‌سازی متن | یکدست‌سازی ی/ک و ارقام عربی به فارسی، حذف کاراکترهای نامرئی جهت متن، حذف اعراب و کشیده، حذف خطوط نویز و بولت‌های اشتباه OCR، حفظ نیم‌فاصله | `app/services/text_cleaner.py` |
| API | `POST /documents` با اعتبارسنجی نوع فایل (۴۱۵)، فایل خالی (۴۰۰) و سقف حجم ۲۰ مگابایت (۴۱۳) | `app/api/documents.py` |
| تست | تست‌های واحد پاک‌سازی و تست‌های API با OCR جعلی (`monkeypatch`) | `tests/` |

### نکات طراحی

- فایل آپلودی با نام یکتا (`uuid4`) ذخیره می‌شود، نه با نام کاربر (جلوگیری از path traversal و بازنویسی).
- تنظیمات از متغیر محیطی خوانده می‌شود (`TESSERACT_CMD`) تا انتقال به Docker ساده باشد.
- endpoint از نوع `def` معمولی است تا OCR سنگین روی thread جدا اجرا شود و سرور قفل نکند.
- جزئیات خطاهای داخلی فقط در لاگ ثبت می‌شود و به کاربر پیام عمومی داده می‌شود.

### یافته‌های آزمایشی

روی یک تصویر نمونه با چیدمان پیچیده (پس‌زمینه رنگی، قاب‌های متعدد، متن کوچک) چند ترکیب پیش‌پردازش و حالت Page Segmentation مقایسه شد:

- بهترین نتیجه: خاکستری + بزرگ‌نمایی ۲ برابر + افزایش کنتراست.
- **باینری کردن تصویر** با وجود تمیزتر دیده شدن، دقت OCR را بدتر کرد.
- حالت `psm 11` برای متن پراکنده (نمودار) و `psm 3` برای متن صفحه‌ای مناسب‌تر است.
- خطاهای تشخیصی تکرارشونده (مثل جابه‌جایی حروفی که فقط در نقطه تفاوت دارند) با پیش‌پردازش ساده رفع نمی‌شوند. این موضوع در فاز ارزیابی با مقایسه موتورهای OCR دیگر و اصلاح متن بررسی می‌شود.

## راه‌اندازی (Windows)

**پیش‌نیازها:** Python 3.12، Git، Tesseract OCR.

```bash
# ۱) نصب Tesseract
winget install UB-Mannheim.TesseractOCR

# ۲) کلون و محیط مجازی
git clone https://github.com/paras2Goodarzi/docintel.git
cd docintel
py -3.12 -m venv .venv
source .venv/Scripts/activate        # Git Bash
# PowerShell: .venv\Scripts\Activate.ps1

# ۳) نصب وابستگی‌ها
pip install -r requirements.txt

# ۴) فایل‌های زبان Tesseract (داخل پروژه، در .gitignore است)
mkdir -p tessdata
curl -L -o tessdata/fas.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/fas.traineddata
cp "/c/Program Files/Tesseract-OCR/tessdata/eng.traineddata" tessdata/
```

### اجرا

```bash
uvicorn app.main:app --reload --port 8080
```

- Swagger: http://127.0.0.1:8080/docs
- بررسی سلامت: `GET /health`

```bash
curl -F "file=@sample.pdf" http://127.0.0.1:8080/documents
```

### تست

```bash
python -m pytest -v
```

## ساختار پروژه

```text
app/
  api/         # مسیرهای FastAPI
  services/    # ocr, text_cleaner
  models/      # schemas (قالب پاسخ API)
  db/          # اتصال و مدل‌های دیتابیس
data/          # raw / processed / eval (محتوا در Git نیست)
scripts/       # اسکریپت‌های آزمایشی
tests/
tessdata/      # فایل‌های زبان Tesseract (در Git نیست)
```

## نقشه راه

- [x] فاز ۰: اسکلت پروژه و `GET /health`
- [x] فاز ۱: OCR فارسی، پاک‌سازی متن، `POST /documents`
- [ ] فاز ۲: ذخیره سند و صفحه‌ها در SQL (SQLAlchemy)
- [ ] فاز ۳: Chunking، embedding و جستجوی معنایی
- [ ] فاز ۴: RAG با مدل لوکال و API
- [ ] فاز ۵: گراف دانش (Neo4j)
- [ ] فاز ۶: ارزیابی و بهبود
- [ ] فاز ۷: Fine-tuning سبک (QLoRA)
- [ ] فاز ۸: Docker Compose و استقرار