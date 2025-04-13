FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY . .

RUN uv pip install --system .

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . .

ENV REDIS_URL=redis://redis
ENV PYTHONUNBUFFERED=1
ENV REFLEX_DEBUG_MODE=False

EXPOSE 8000

# Needed until Reflex properly passes SIGTERM on backend
STOPSIGNAL SIGKILL

# Apply migrations if alembic directory exists, then start the app
CMD bash -c "[ -d alembic ] && reflex db migrate; reflex run --env prod --backend-only --loglevel debug"
