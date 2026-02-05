from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    data_dir: str
    lancedb_dir: str
    streamlit_port: int


def get_settings() -> Settings:
    data_dir = os.getenv("APP_DATA_DIR", "/app/data")
    lancedb_dir = os.getenv("LANCEDB_DIR", "/app/lancedb")
    streamlit_port = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))

    return Settings(
        data_dir=data_dir,
        lancedb_dir=lancedb_dir,
        streamlit_port=streamlit_port,
    )
