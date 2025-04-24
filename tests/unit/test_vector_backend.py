# tests/unit/test_vector_backend.py
from PRISMAgent.storage.vector_backend import VectorStore
import numpy as np

def test_upsert_and_query_roundtrip(monkeypatch):
    monkeypatch.setenv("VECTOR_PROVIDER", "redis")
    store = VectorStore()
    vec = np.random.rand(512).tolist()
    store.upsert("42", vec, {"foo": "bar"})
    hits = store.query(vec, k=1)
    assert hits and hits[0][0]["foo"] == "bar"
