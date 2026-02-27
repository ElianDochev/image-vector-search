# Picture Similarities

Image similarity search app: upload a query image and retrieve visually similar images from a local dataset.

It follows the approach in `plan.md`:
- Extract embeddings with **ResNet-50** (`microsoft/resnet-50` via Hugging Face Transformers)
- Store/search embeddings in **LanceDB** (local vector database)
- Provide a minimal **Streamlit** UI for interactive search

## What runs in Docker

- `app`: Python + Streamlit app (CPU-only)

LanceDB stores its data on disk under `./lancedb/` (mounted into the container).

## Quickstart

1) Create your `.env` from the example:

```bash
cp .env.example .env
```

2) Put some images under `./data/` (or `./static/`) (any nested folders are fine).

If you used `./static/`, set `APP_DATA_DIR=/app/static` in `.env`.

3) Start services:

```bash
docker compose up --build
```

4) Ingest embeddings into the DB via Compose:

```bash
docker compose run --rm ingest
```

5) Open the UI:

- http://localhost:8501

Upload an image and click **Search**.

## Demo

![Demo](static/demo.gif)

## Test images

The folder `./test-img/` contains a few images you can use as query uploads in the UI.

## Startup indexing behavior

On the first **Search** request (and only if LanceDB is empty), the app will automatically:
- scan the configured `APP_DATA_DIR` (commonly `/app/static`)
- compute embeddings
- write them into LanceDB under `./lancedb/`

You can still run manual ingestion any time via `docker compose run --rm ingest`.

## Notes

- The DB stores **relative image paths** (relative to `APP_DATA_DIR`).
- The dataset folders are mounted into the `app` container at `/app/data` and `/app/static`.
- LanceDB files live in `./lancedb/` on the host.
- If you change the dataset contents, re-run the ingestion script.

## Common troubleshooting

- **No results / empty DB**: run `docker compose run --rm ingest`.
- **Big downloads on first run**: the ResNet-50 model weights are downloaded the first time embeddings are computed.
