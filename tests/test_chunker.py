import pytest

from app.services.chunker import chunk_pages, chunk_text


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []


def test_short_text_is_single_chunk():
    assert chunk_text("سلام دنیا") == ["سلام دنیا"]


def test_chunks_respect_max_chars():
    text = " ".join(f"کلمه{i}" for i in range(500))
    chunks = chunk_text(text, max_chars=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_consecutive_chunks_overlap():
    text = " ".join(f"کلمه{i}" for i in range(500))
    chunks = chunk_text(text, max_chars=200, overlap=40)
    # ابتدای هر تکه باید توی تکه قبلی هم باشه
    for prev, cur in zip(chunks, chunks[1:]):
        assert cur[:15] in prev


def test_no_content_is_lost():
    words = [f"w{i}" for i in range(400)]
    chunks = chunk_text(" ".join(words), max_chars=200, overlap=40)
    seen = set(" ".join(chunks).split())
    assert seen == set(words)


def test_cuts_on_sentence_boundary():
    text = " ".join(["این یک جمله است."] * 100)
    chunks = chunk_text(text, max_chars=200, overlap=40)
    assert all(c.endswith(".") for c in chunks[:-1])


def test_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("متن", max_chars=100, overlap=60)


def test_chunk_pages_keeps_page_numbers_and_global_index():
    long_text = " ".join(f"کلمه{i}" for i in range(300))
    chunks = chunk_pages([(1, "صفحه کوتاه"), (2, long_text)], max_chars=200, overlap=40)
    assert chunks[0].page_no == 1 and chunks[0].text == "صفحه کوتاه"
    assert all(c.page_no == 2 for c in chunks[1:])
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))