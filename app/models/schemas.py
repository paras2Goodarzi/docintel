from pydantic import BaseModel


class PageOut(BaseModel):
    page_no: int
    text: str


class DocumentOut(BaseModel):
    document_id: str
    filename: str
    num_pages: int
    pages: list[PageOut]