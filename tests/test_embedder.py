import numpy as np

from app.services import embedder


class FakeModel:
    def __init__(self):
        self.seen: list[str] = []

    def encode(self, texts, **kwargs):
        self.seen = texts
        return np.ones((len(texts), 3))


def test_passages_get_passage_prefix(monkeypatch):
    fake = FakeModel()
    monkeypatch.setattr(embedder, "get_model", lambda: fake)

    vectors = embedder.embed_passages(["الف", "ب"])

    assert fake.seen == ["passage: الف", "passage: ب"]
    assert len(vectors) == 2 and len(vectors[0]) == 3


def test_query_gets_query_prefix(monkeypatch):
    fake = FakeModel()
    monkeypatch.setattr(embedder, "get_model", lambda: fake)

    vector = embedder.embed_query("سؤال")

    assert fake.seen == ["query: سؤال"]
    assert len(vector) == 3


def test_empty_passages_skip_model(monkeypatch):
    def boom():
        raise AssertionError("model should not be loaded")

    monkeypatch.setattr(embedder, "get_model", boom)
    assert embedder.embed_passages([]) == []