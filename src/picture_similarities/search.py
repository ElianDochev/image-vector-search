from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pyarrow as pa
import lancedb

from picture_similarities.config import get_settings


@dataclass(frozen=True)
class SearchResult:
    image_path: str
    score: float


TABLE_NAME = "images"
EMBEDDING_DIM = 2048


def _schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("image_path", pa.string(), nullable=False),
            pa.field("embedding", pa.list_(pa.float32(), list_size=EMBEDDING_DIM), nullable=False),
        ]
    )


def _get_table():
    settings = get_settings()
    db = lancedb.connect(settings.lancedb_dir)
    names = set(db.table_names())
    if TABLE_NAME in names:
        return db.open_table(TABLE_NAME)
    return db.create_table(TABLE_NAME, schema=_schema())


def upsert_image(image_path: str, embedding: np.ndarray) -> None:
    table = _get_table()
    vec = embedding.astype(np.float32).reshape(-1)
    if vec.shape[0] != EMBEDDING_DIM:
        raise ValueError(f"Expected embedding dim {EMBEDDING_DIM}, got {vec.shape[0]}")

    # LanceDB doesn't have a native upsert-by-key in all versions; simplest is delete+insert.
    # This keeps the ingestion idempotent for repeated runs.
    table.delete(f"image_path = '{image_path.replace("'", "''")}'")
    table.add([{"image_path": image_path, "embedding": vec.tolist()}])


def query_similar(
    query_embedding: np.ndarray, top_k: int = 5
) -> list[SearchResult]:
    table = _get_table()
    q = query_embedding.astype(np.float32).reshape(-1)
    if q.shape[0] != EMBEDDING_DIM:
        raise ValueError(f"Expected embedding dim {EMBEDDING_DIM}, got {q.shape[0]}")

    rows = table.search(q.tolist()).metric("cosine").limit(int(top_k)).to_list()
    results: list[SearchResult] = []
    for row in rows:
        image_path = str(row["image_path"])
        # LanceDB returns a distance for cosine; convert to similarity score for display.
        distance = float(row.get("_distance", 0.0))
        score = 1.0 - distance
        results.append(SearchResult(image_path=image_path, score=score))
    return results
