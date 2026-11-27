import os
from functools import lru_cache

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
EMBEDDING_DIM = 384  # ابعاد بردار خروجی این مدل


@lru_cache(maxsize=1)
def get_model():
    """مدل را فقط یک بار (دفعه اول که لازم شد) بارگذاری می‌کند."""
    # import اینجاست تا بقیه برنامه و تست‌ها بدون نیاز به لود torch سریع بالا بیان
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """متن تکه‌های سند را به بردار تبدیل می‌کند."""
    if not texts:
        return []
    vectors = get_model().encode(
        [f"passage: {t}" for t in texts],
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """سؤال یا عبارت جستجو را به بردار تبدیل می‌کند."""
    vector = get_model().encode(
        [f"query: {text}"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vector[0].tolist()