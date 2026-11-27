from fastapi.testclient import TestClient

from app.api import documents
from app.main import app
from app.services.ocr import PageResult

client = TestClient(app)


def test_rejects_unsupported_file_type():
    r = client.post("/documents", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_rejects_empty_file():
    r = client.post("/documents", files={"file": ("a.png", b"", "image/png")})
    assert r.status_code == 400


def test_returns_pages(monkeypatch, tmp_path):
    # به‌جای OCR واقعی (کند و وابسته به Tesseract) یه نسخه جعلی می‌ذاریم
    monkeypatch.setattr(documents, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(documents, "ocr_file", lambda path: [PageResult(1, "سلام")])

    r = client.post("/documents", files={"file": ("a.png", b"fake", "image/png")})

    assert r.status_code == 200
    body = r.json()
    assert body["num_pages"] == 1
    assert body["pages"][0]["text"] == "سلام"
    assert body["filename"] == "a.png"