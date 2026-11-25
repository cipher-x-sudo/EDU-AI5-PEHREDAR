# syntax=docker/dockerfile:1
FROM python:3.11-slim AS gateway

WORKDIR /app
COPY pyproject.toml README.md ./
COPY pehredar ./pehredar
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-build-isolation --timeout 300 --retries 10 .

EXPOSE 8000
CMD ["uvicorn", "pehredar.app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM gateway AS classifier-gateway
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 ".[classifier]"

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime AS trainer
WORKDIR /app
COPY pyproject.toml README.md ./
COPY pehredar ./pehredar
COPY scripts ./scripts
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 --no-build-isolation ".[training,embeddings]"

# Gateway with L2 (routed DeBERTa + XLM-R v2) on GPU; enabled with PEHREDAR_L2=1.
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime AS gateway-gpu
WORKDIR /app
COPY pyproject.toml README.md ./
COPY pehredar ./pehredar
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 --no-build-isolation ".[classifier]"
EXPOSE 8000
CMD ["uvicorn", "pehredar.app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM gateway AS dashboard
COPY dashboard.py ./dashboard.py
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 ".[dashboard]"
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]

FROM gateway AS data
COPY scripts ./scripts
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 ".[data]"

FROM gateway AS tests
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 300 --retries 10 pytest

FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
RUN npm run build

FROM nginx:alpine AS frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html
EXPOSE 80
