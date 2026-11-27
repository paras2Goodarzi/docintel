import re
from collections.abc import Iterable
from dataclasses import dataclass

# پایان جمله: نقطه، علامت تعجب، سؤال (انگلیسی و فارسی)، نقطه‌ویرگول، به شرط اینکه بعدش فاصله بیاد
_SENTENCE_END = re.compile(r"[.!?؟؛](?=\s)")


@dataclass
class TextChunk:
    chunk_index: int  # شماره تکه در کل سند (از ۰)
    page_no: int      # تکه از کدوم صفحه اومده (برای ارجاع/citation)
    text: str


def _best_cut(text: str, start: int, end: int) -> int:
    """بهترین نقطه برش در نیمه دوم پنجره [start, end) را پیدا می‌کند.

    اولویت: پایان پاراگراف، پایان جمله، پایان خط، فاصله بین کلمه‌ها.
    اگر هیچ‌کدام نبود، برش سخت در end.
    """
    window = text[start:end]
    floor = len(window) // 2  # قبل از نیمه پنجره برش نمی‌زنیم تا تکه‌ها خیلی کوتاه نشن

    pos = window.rfind("\n\n")
    if pos >= floor:
        return start + pos

    last = None
    for m in _SENTENCE_END.finditer(window):
        if m.start() >= floor:
            last = m
    if last is not None:
        return start + last.end()

    pos = window.rfind("\n")
    if pos >= floor:
        return start + pos

    pos = window.rfind(" ")
    if pos >= floor:
        return start + pos

    return end


def chunk_text(text: str, max_chars: int = 800, overlap: int = 150) -> list[str]:
    """متن را به تکه‌های حداکثر max_chars کاراکتری با هم‌پوشانی overlap تقسیم می‌کند."""
    if not 0 <= overlap < max_chars // 2:
        raise ValueError("overlap must be >= 0 and less than half of max_chars")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + max_chars, n)
        if end < n:
            end = _best_cut(text, start, end)

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break

        # شروع تکه بعدی: overlap کاراکتر عقب‌تر، و جلو رفتن تا اولین فاصله (تا وسط کلمه شروع نشه)
        next_start = end - overlap
        space = text.find(" ", next_start, end)
        if space != -1:
            next_start = space + 1
        start = next_start

    return chunks


def chunk_pages(
    pages: Iterable[tuple[int, str]], max_chars: int = 800, overlap: int = 150
) -> list[TextChunk]:
    """هر صفحه را جدا chunk می‌کند تا هر تکه شماره صفحه خودش را داشته باشد."""
    result: list[TextChunk] = []
    for page_no, text in pages:
        for piece in chunk_text(text, max_chars, overlap):
            result.append(TextChunk(chunk_index=len(result), page_no=page_no, text=piece))
    return result