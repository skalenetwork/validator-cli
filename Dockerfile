FROM ubuntu:24.04 AS builder

ENV UV_PYTHON_INSTALL_DIR=/opt/python

COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv venv --python 3.14.10 /opt/venv && \
    uv pip install --python /opt/venv --no-cache ".[dev]"

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends binutils git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /opt/python /opt/python
COPY --from=builder /opt/venv /opt/venv

COPY . .

ENV PATH="/opt/venv/bin:$PATH"
