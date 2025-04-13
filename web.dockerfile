FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -fsSL https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy the application code
COPY . .

# Create virtual environment manually first
RUN python -m venv .venv
# Then use uv with the created environment
RUN uv sync --all-extras
RUN uv run reflex export --frontend-only --no-zip

FROM nginx:alpine

# Copy the exported static files to nginx
COPY --from=builder /app/.web/_static /usr/share/nginx/html
# Copy the nginx configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
