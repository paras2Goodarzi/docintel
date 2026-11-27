from fastapi import FastAPI
from app.api import documents

app = FastAPI(title="Persian Document Intelligence Platform")
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}