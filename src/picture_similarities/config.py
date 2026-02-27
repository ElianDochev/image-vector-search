from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass(frozen=True)
class Settings:
    data_dir: str
    lancedb_dir: str
    streamlit_port: int


def _has_images(directory: Path) -> bool:
    if not directory.exists() or not directory.is_dir():
        return False

    for path in directory.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            return True
    return False


def _resolve_default_data_dir() -> str:
    candidates = [Path("/app/data"), Path("/app/static"), Path("data"), Path("static")]

    for candidate in candidates:
        if _has_images(candidate):
            return str(candidate)

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return str(candidate)

    return "/app/data"


def get_settings() -> Settings:
    data_dir = os.getenv("APP_DATA_DIR") or _resolve_default_data_dir()
    lancedb_dir = os.getenv("LANCEDB_DIR", "/app/lancedb")
    streamlit_port = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))

    return Settings(
        data_dir=data_dir,
        lancedb_dir=lancedb_dir,
        streamlit_port=streamlit_port,
    )
