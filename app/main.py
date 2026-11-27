from fastapi import FastAPI
from app.api import documents

from contextlib import asynccontextmanager
from app.db import models  # noqa: F401  (برای اینکه مدل‌ها ثبت بشن)
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # جدول‌هایی که وجود ندارن ساخته می‌شن
    yield
    
app = FastAPI(title="Persian Document Intelligence Platform")
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}