FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -fsSL https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy the application code
COPY . .

# Create virtual environment and install dependencies in one step
RUN uv sync --all-extras

ENV REDIS_URL=redis://redis
ENV PYTHONUNBUFFERED=1
ENV REFLEX_DEBUG_MODE=False

EXPOSE 8000

# Needed until Reflex properly passes SIGTERM on backend
STOPSIGNAL SIGKILL

# Apply migrations if alembic directory exists, then start the app
CMD bash -c "[ -d alembic ] && uv run reflex db migrate; uv run reflex run --env prod --backend-only --loglevel debug"
