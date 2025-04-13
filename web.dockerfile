FROM python:3.12-slim AS builder

WORKDIR /app

COPY . .

# Install UV
RUN apt-get update && apt-get install --no-install-recommends -y curl unzip && \
    curl -fsSL https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies from pyproject.toml
# RUN uv venv
RUN uv pip install -r pyproject.toml --system
RUN reflex export --frontend-only --no-zip

FROM nginx:alpine

COPY --from=builder /app/.web/_static /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
