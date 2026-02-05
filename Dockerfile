FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY app /app/app
COPY scripts /app/scripts

RUN python -m pip install --no-cache-dir -U pip \
  && python -m pip install --no-cache-dir .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
