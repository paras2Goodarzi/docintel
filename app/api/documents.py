import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Chunk, Document, Page
from app.models.schemas import DocumentList, DocumentOut, DocumentSummary, PageOut
from app.services.chunker import chunk_pages
from app.services.ocr import ocr_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MAX_BYTES = 20 * 1024 * 1024  # حداکثر ۲۰ مگابایت


@router.post("", response_model=DocumentOut)
def create_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
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

    # ۳) ذخیره فایل با اسم امن و یکتا
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

    # ۵) chunk کردن و ذخیره توی دیتابیس
    filename = file.filename or saved_path.name
    text_chunks = chunk_pages([(p.page_no, p.text) for p in pages])
    document = Document(
        id=document_id,
        filename=filename,
        stored_path=saved_path.name,
        num_pages=len(pages),
        status="done",
        pages=[Page(page_no=p.page_no, text=p.text) for p in pages],
        chunks=[
            Chunk(page_no=c.page_no, chunk_index=c.chunk_index, text=c.text)
            for c in text_chunks
        ],
    )
    try:
        db.add(document)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("DB save failed for %s", document_id)
        raise HTTPException(status_code=500, detail="Failed to save document")

    # ۶) ساخت پاسخ
    return DocumentOut(
        document_id=document_id,
        filename=filename,
        num_pages=len(pages),
        pages=[PageOut(page_no=p.page_no, text=p.text) for p in pages],
    )


@router.get("", response_model=DocumentList)
def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Document)) or 0
    rows = db.scalars(
        select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return DocumentList(
        total=total,
        items=[
            DocumentSummary(
                document_id=d.id,
                filename=d.filename,
                num_pages=d.num_pages,
                status=d.status,
                created_at=d.created_at,
            )
            for d in rows
        ],
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut(
        document_id=doc.id,
        filename=doc.filename,
        num_pages=doc.num_pages,
        pages=[PageOut(page_no=p.page_no, text=p.text) for p in doc.pages],
    )