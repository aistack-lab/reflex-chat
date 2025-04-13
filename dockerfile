FROM python:3.12-slim

ENV REDIS_URL=redis://redis
ENV PYTHONUNBUFFERED=1
ENV REFLEX_DEBUG_MODE=False

WORKDIR /app
COPY . .

# Install UV
RUN apt-get update && apt-get install --no-install-recommends -y curl && \
    curl -fsSL https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies from pyproject.toml
# RUN uv venv
RUN uv pip install -r pyproject.toml --system

EXPOSE 8000

# Needed until Reflex properly passes SIGTERM on backend
STOPSIGNAL SIGKILL

ENTRYPOINT ["reflex", "run", "--env", "prod", "--backend-only", "--loglevel", "debug"]
