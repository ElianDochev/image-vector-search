from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from PIL import Image

from picture_similarities.config import get_settings
from picture_similarities.embedding import compute_embedding
from picture_similarities.search import query_similar


def resolve_image_path(data_dir: Path, stored_rel_path: str) -> Path:
    # We store relative paths in DB. Resolve safely under data_dir.
    candidate = (data_dir / stored_rel_path).resolve()
    if not str(candidate).startswith(str(data_dir.resolve())):
        raise ValueError("Unsafe image path in DB")
    return candidate


def main() -> None:
    settings = get_settings()
    data_dir = Path(settings.data_dir)

    st.set_page_config(page_title="Picture Similarities", layout="wide")
    st.title("Picture Similarities")
    st.write(
        "Upload an image and retrieve the most visually similar images from the dataset in ./data."
    )

    top_k = st.slider("Top-K results", min_value=1, max_value=20, value=5, step=1)
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp", "bmp"])

    if uploaded is None:
        st.info("Upload an image to search.")
        return

    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Query image", use_container_width=False)

    if st.button("Search", type="primary"):
        if not data_dir.exists():
            st.error(f"Data dir not found: {data_dir}. Mount ./data into the container.")
            return

        query_emb = compute_embedding(image)
        results = query_similar(query_emb, top_k=top_k)

        if not results:
            st.warning("No images in DB yet. Run scripts/get_embeddings.py first.")
            return

        st.subheader("Results")
        cols = st.columns(min(5, len(results)))
        for i, res in enumerate(results):
            with cols[i % len(cols)]:
                st.caption(f"score={res.score:.4f}")
                st.caption(res.image_path)
                try:
                    p = resolve_image_path(data_dir, res.image_path)
                    if p.exists():
                        st.image(str(p), use_container_width=True)
                    else:
                        st.warning("File missing on disk")
                except Exception as e:  # noqa: BLE001
                    st.warning(str(e))


if __name__ == "__main__":
    # Streamlit executes this file; keep top-level minimal.
    main()
