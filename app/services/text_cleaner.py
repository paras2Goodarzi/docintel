import re
import unicodedata

# کاراکترهای نامرئی که OCR یا سیستم‌عامل اضافه می‌کنه و باید حذف بشن.
# نیم‌فاصله (U+200C) عمداً توی این لیست نیست، چون توی فارسی معنی داره (مثل «می‌خواهم»).
INVISIBLE_CHARS = dict.fromkeys(
    map(
        ord,
        "\u200b"  # zero-width space
        "\u200d"  # zero-width joiner
        "\u200e\u200f"  # علامت‌های جهت LRM و RLM
        "\u202a\u202b\u202c\u202d\u202e"  # کنترل‌های جهت متن
        "\u2066\u2067\u2068\u2069"  # ایزوله‌های جهت متن
        "\ufeff",  # BOM
    )
)

# یکدست‌سازی حروف عربی به فارسی + ارقام عربی به فارسی
CHAR_MAP = {
    "\u064a": "\u06cc",  # ي عربی -> ی فارسی
    "\u0649": "\u06cc",  # ى (الف مقصوره) -> ی فارسی
    "\u0643": "\u06a9",  # ك عربی -> ک فارسی
}
for i in range(10):
    CHAR_MAP[chr(0x0660 + i)] = chr(0x06F0 + i)  # ٠-٩ عربی -> ۰-۹ فارسی
CHAR_TABLE = str.maketrans(CHAR_MAP)

# اعراب (فتحه، کسره، ...) و کشیده (ـ)
DIACRITICS_RE = re.compile(r"[\u064B-\u0652\u0640]")

# علامت‌های شبه‌بولت اول خط که OCR از دایره‌های بولت می‌سازه
BULLET_RE = re.compile(r"^\s*[•©*|·\u06F0]+\s+")


def clean_text(text: str, min_alnum: int = 2) -> str:
    """متن خروجی OCR را تمیز و نرمال می‌کند.

    min_alnum: خطی که کمتر از این تعداد حرف/رقم داشته باشد آشغال حساب می‌شود.
    """
    # ۱) نرمال‌سازی یونیکد (فرم‌های ظاهری حروف عربی به حرف پایه تبدیل می‌شن)
    text = unicodedata.normalize("NFKC", text)

    # ۲) حذف کاراکترهای نامرئی
    text = text.translate(INVISIBLE_CHARS)

    # ۳) یکدست‌سازی ی/ک و ارقام
    text = text.translate(CHAR_TABLE)

    # ۴) حذف اعراب و کشیده
    text = DIACRITICS_RE.sub("", text)

    # ۵) یکدست‌سازی پایان خط‌ها
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # ۶) پاک‌سازی خط‌به‌خط
    lines = []
    for line in text.split("\n"):
        line = BULLET_RE.sub("", line)
        line = re.sub(r"[ \t]+", " ", line).strip()
        if sum(ch.isalnum() for ch in line) < min_alnum:
            lines.append("")  # خط آشغال -> خط خالی
            continue
        lines.append(line)
    text = "\n".join(lines)

    # ۷) حداکثر یک خط خالی پشت سر هم
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()