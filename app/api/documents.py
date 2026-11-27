import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import DocumentOut, PageOut
from app.services.ocr import ocr_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_BYTES = 20 * 1024 * 1024  # حداکثر ۲۰ مگابایت


@router.post("", response_model=DocumentOut)
def create_document(file: UploadFile = File(...)):
    # ۱) بررسی نوع فایل
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {suffix or 'unknown'}")

    # ۲) خوندن محتوا با سقف حجم
    content = file.file.read(MAX_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    # ۳) ذخیره با اسم امن و یکتا
    document_id = uuid.uuid4().hex
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"{document_id}{suffix}"
    saved_path.write_bytes(content)

    # ۴) اجرای OCR
    try:
        pages = ocr_file(saved_path)
    except Exception:
        logger.exception("OCR failed for %s", saved_path)
        raise HTTPException(status_code=500, detail="OCR processing failed")

    # ۵) ساخت پاسخ
    return DocumentOut(
        document_id=document_id,
        filename=file.filename or saved_path.name,
        num_pages=len(pages),
        pages=[PageOut(page_no=p.page_no, text=p.text) for p in pages],
    )