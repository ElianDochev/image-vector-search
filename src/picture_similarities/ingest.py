from __future__ import annotations

import os
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from picture_similarities.embedding import compute_embedding
from picture_similarities.search import EMBEDDING_DIM, _get_table, upsert_image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def iter_images(data_dir: Path):
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            yield path


def is_table_empty() -> bool:
    table = _get_table()
    # LanceDB Table API differs slightly across versions; try a few ways.
    for attr in ("count_rows", "count"):  # pragma: no branch
        fn = getattr(table, attr, None)
        if callable(fn):
            return int(fn()) == 0

    # Fallback: cheap probe via search
    probe = [0.0] * EMBEDDING_DIM
    rows = table.search(probe).limit(1).to_list()
    return len(rows) == 0


def ingest_directory(data_dir: Path, *, show_progress: bool = True) -> int:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data dir not found: {data_dir}")

    image_paths = list(iter_images(data_dir))
    if not image_paths:
        return 0

    iterator = tqdm(image_paths, desc="Embedding images") if show_progress else image_paths
    inserted = 0
    for path in iterator:
        rel_path = os.path.relpath(path, data_dir)
        try:
            with Image.open(path) as img:
                emb = compute_embedding(img)
            upsert_image(rel_path, emb)
            inserted += 1
        except Exception as e:  # noqa: BLE001
            if show_progress and hasattr(iterator, "write"):
                iterator.write(f"Skipping {path}: {e}")
    return inserted
