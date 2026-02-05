from __future__ import annotations

import os
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from picture_similarities.config import get_settings
from picture_similarities.embedding import compute_embedding
from picture_similarities.search import upsert_image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def iter_images(data_dir: Path):
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            yield path


def main() -> None:
    settings = get_settings()
    data_dir = Path(settings.data_dir)

    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}")

    image_paths = list(iter_images(data_dir))
    if not image_paths:
        raise SystemExit(
            f"No images found under {data_dir}. Put images in ./data or ./static and set APP_DATA_DIR accordingly."
        )

    for path in tqdm(image_paths, desc="Embedding images"):
        rel_path = os.path.relpath(path, data_dir)
        try:
            with Image.open(path) as img:
                emb = compute_embedding(img)
            upsert_image(rel_path, emb)
        except Exception as e:  # noqa: BLE001
            tqdm.write(f"Skipping {path}: {e}")


if __name__ == "__main__":
    main()
