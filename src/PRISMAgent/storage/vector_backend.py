# vector_backend.py   (≈120 LOC including imports & docstring)
from __future__ import annotations
import os, json, numpy as np
from typing import List, Dict, Tuple

_BACKEND = os.getenv("VECTOR_PROVIDER", "pinecone")  # "pinecone" or "redis"
_EMBED_DIM = int(os.getenv("EMBED_DIM", 512))

if _BACKEND == "pinecone":
    import pinecone
    pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),
                  environment=os.getenv("PINECONE_ENV", "us-west-1"))
    _index = pinecone.Index(os.getenv("PINECONE_INDEX", "prisma-memory"))

    def _upsert(i, v, m): _index.upsert([{"id": i, "values": v, "metadata": m}])
    def _query(v, k):     return _index.query(v, top_k=k, include_metadata=True)

else:                                       # redis-vector
    from redisvl.vectorstore import RedisVectorStore
    _index = RedisVectorStore(
        name=os.getenv("REDIS_INDEX", "prisma-memory"),
        prefix="mem", dim=_EMBED_DIM, distance_metric="COSINE",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )
    if not _index.exists(): _index.create_index()
    def _upsert(i, v, m): _index.upsert_texts(v, ids=[i], metadata=[m])
    def _query(v, k):     return _index.query(v, k=k, include_metadata=True)

class VectorStore:
    """Thin wrapper surfaced to agents via registry_factory()."""
    def upsert(self, uid: str, vec: List[float], meta: Dict): _upsert(uid, vec, meta)
    def query(self, vec: List[float], k: int = 5):            return _query(vec, k)
