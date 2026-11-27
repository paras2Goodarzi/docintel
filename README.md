خلاصه فاز ۱

هدف فاز: فایل (عکس یا PDF) وارد بشه و متن تمیز فارسی از اون دربیاد، پشت یه API.

گام	چی ساختیم	فایل اصلی
۰	اسکلت پروژه، Git، venv و GET /health	app/main.py
۱	نصب Tesseract با زبان فارسی (داخل پروژه) و اولین OCR	scripts/ocr_test.py
۱-ب	آزمایش پیش‌پردازش و PSM روی عکس واقعی	scripts/ocr_compare.py
۳	پاک‌سازی متن (یکدست‌سازی ی/ک و ارقام، حذف کاراکترهای نامرئی و خطوط آشغال) + ۷ تست	app/services/text_cleaner.py
۲	خوندن PDF صفحه‌به‌صفحه و یکی کردن OCR و پاک‌سازی در یک سرویس	app/services/ocr.py
۴	POST /documents با اعتبارسنجی نوع و حجم فایل و ۳ تست	app/api/documents.py
