from fastapi import FastAPI

app = FastAPI(title="Persian Document Intelligence Platform")


@app.get("/health")
def health():
    return {"status": "ok"}