from __future__ import annotations

import functools

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, ResNetModel


MODEL_ID = "microsoft/resnet-50"


@functools.lru_cache(maxsize=1)
def _load() -> tuple[AutoImageProcessor, ResNetModel]:
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = ResNetModel.from_pretrained(MODEL_ID)
    model.eval()
    return processor, model


def compute_embedding(image: Image.Image) -> np.ndarray:
    processor, model = _load()

    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

        # ResNetModel commonly returns a spatial feature map in last_hidden_state:
        #   (batch, channels=2048, h, w)
        # We convert it into a single vector via global average pooling.
        if getattr(outputs, "last_hidden_state", None) is not None:
            pooled = outputs.last_hidden_state.mean(dim=(2, 3))  # (batch, 2048)
        elif getattr(outputs, "pooler_output", None) is not None:
            pooled = outputs.pooler_output
        else:
            raise RuntimeError("ResNet outputs did not include last_hidden_state/pooler_output")

        vec = pooled[0].detach().cpu().numpy().astype(np.float32).reshape(-1)

    if vec.ndim != 1:
        raise RuntimeError(f"Embedding must be 1-D, got shape={vec.shape}")
    if vec.shape[0] != 2048:
        raise RuntimeError(f"Embedding must be length 2048, got length={vec.shape[0]}")

    # L2 normalize for cosine distance
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec = vec / norm
    return vec
