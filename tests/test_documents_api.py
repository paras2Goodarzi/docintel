from app.api import documents
from app.db.models import Document, Page
from app.services.ocr import PageResult


def _upload(client, monkeypatch, tmp_path, filename, texts):
    """یه سند با OCR جعلی آپلود می‌کنه و document_id رو برمی‌گردونه."""
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        documents,
        "ocr_file",
        lambda path: [PageResult(i, t) for i, t in enumerate(texts, start=1)],
    )
    r = client.post("/documents", files={"file": (filename, b"fake", "application/pdf")})
    assert r.status_code == 200
    return r.json()["document_id"]


def test_rejects_unsupported_file_type(client):
    r = client.post("/documents", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_rejects_empty_file(client):
    r = client.post("/documents", files={"file": ("a.png", b"", "image/png")})
    assert r.status_code == 400


def test_returns_pages(client, monkeypatch, tmp_path):
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(documents, "ocr_file", lambda path: [PageResult(1, "سلام")])

    r = client.post("/documents", files={"file": ("a.png", b"fake", "image/png")})

    assert r.status_code == 200
    body = r.json()
    assert body["num_pages"] == 1
    assert body["pages"][0]["text"] == "سلام"
    assert body["filename"] == "a.png"


def test_saves_document_and_pages_in_db(client, session_factory, monkeypatch, tmp_path):
    doc_id = _upload(client, monkeypatch, tmp_path, "c.pdf", ["صفحه اول", "صفحه دوم"])

    with session_factory() as db:
        doc = db.get(Document, doc_id)
        assert doc is not None
        assert doc.filename == "c.pdf"
        assert doc.num_pages == 2
        assert doc.status == "done"
        assert [p.text for p in doc.pages] == ["صفحه اول", "صفحه دوم"]
        assert db.query(Page).count() == 2


def test_saves_chunks_in_db(client, session_factory, monkeypatch, tmp_path):
    long_text = " ".join(f"کلمه{i}" for i in range(600))
    doc_id = _upload(client, monkeypatch, tmp_path, "c.pdf", ["کوتاه", long_text])

    with session_factory() as db:
        doc = db.get(Document, doc_id)
        assert len(doc.chunks) > 2
        assert [c.chunk_index for c in doc.chunks] == list(range(len(doc.chunks)))
        assert doc.chunks[0].page_no == 1
        assert doc.chunks[0].text == "کوتاه"
        assert all(c.page_no == 2 for c in doc.chunks[1:])


def test_list_documents_empty(client):
    r = client.get("/documents")
    assert r.status_code == 200
    assert r.json() == {"total": 0, "items": []}


def test_list_documents_newest_first_with_total(client, monkeypatch, tmp_path):
    _upload(client, monkeypatch, tmp_path, "first.pdf", ["الف"])
    _upload(client, monkeypatch, tmp_path, "second.pdf", ["ب", "ج"])

    body = client.get("/documents").json()

    assert body["total"] == 2
    assert [d["filename"] for d in body["items"]] == ["second.pdf", "first.pdf"]
    assert body["items"][0]["num_pages"] == 2
    assert "pages" not in body["items"][0]


def test_list_documents_pagination(client, monkeypatch, tmp_path):
    for name in ("a.pdf", "b.pdf", "c.pdf"):
        _upload(client, monkeypatch, tmp_path, name, ["x"])

    body = client.get("/documents", params={"limit": 2, "offset": 2}).json()

    assert body["total"] == 3
    assert len(body["items"]) == 1


def test_list_documents_rejects_bad_limit(client):
    assert client.get("/documents", params={"limit": 0}).status_code == 422
    assert client.get("/documents", params={"limit": 101}).status_code == 422


def test_get_document_returns_pages_in_order(client, monkeypatch, tmp_path):
    doc_id = _upload(client, monkeypatch, tmp_path, "c.pdf", ["صفحه اول", "صفحه دوم"])

    r = client.get(f"/documents/{doc_id}")

    assert r.status_code == 200
    body = r.json()
    assert body["document_id"] == doc_id
    assert [p["text"] for p in body["pages"]] == ["صفحه اول", "صفحه دوم"]


def test_get_document_not_found(client):
    r = client.get("/documents/does-not-exist")
    assert r.status_code == 404