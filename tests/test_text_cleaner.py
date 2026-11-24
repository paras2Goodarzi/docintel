from app.services.text_cleaner import clean_text


def test_removes_direction_marks():
    assert clean_text("\u200eMQ\u200f") == "MQ"


def test_unifies_arabic_letters_to_persian():
    # ي (عربی) و ك (عربی) باید ی و ک فارسی بشن
    assert clean_text("\u064a\u0643") == "\u06cc\u06a9"


def test_converts_arabic_digits_to_persian():
    assert clean_text("\u0661\u0662\u0663") == "\u06f1\u06f2\u06f3"


def test_keeps_zwnj():
    text = "می\u200cخواهم"
    assert clean_text(text) == text


def test_removes_junk_lines():
    assert clean_text("—\n=\nسلام") == "سلام"


def test_strips_bullet_marker():
    assert clean_text("\u06f0 سرویس ثبت احوال") == "سرویس ثبت احوال"


def test_collapses_whitespace_and_blank_lines():
    assert clean_text("سلام    دنیا\n\n\n\n\nخداحافظ") == "سلام دنیا\n\nخداحافظ"