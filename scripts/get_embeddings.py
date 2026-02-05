from __future__ import annotations

from pathlib import Path

from picture_similarities.config import get_settings
from picture_similarities.ingest import ingest_directory


def main() -> None:
    settings = get_settings()
    data_dir = Path(settings.data_dir)

    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}")

    inserted = ingest_directory(data_dir, show_progress=True)
    if inserted == 0:
        raise SystemExit(
            f"No images found under {data_dir}. Put images in ./data or ./static and set APP_DATA_DIR accordingly."
        )


if __name__ == "__main__":
    main()
