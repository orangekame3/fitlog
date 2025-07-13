# Multi-stage build for smaller final image
FROM python:3.11-slim as builder
RUN apt update && apt install curl build-essential -y
# Install uv
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN curl --proto '=https' --tlsv1.2 -LsSf https://github.com/astral-sh/uv/releases/download/0.5.24/uv-installer.sh | sh
ENV PATH="/root/.local/bin/:$PATH"
# Set working directory
WORKDIR /app

# Copy dependency filess
COPY pyproject.toml README.md ./

# Install dependencies
RUN uv sync --no-dev

# Production stage
FROM python:3.11-slim

# Install timezone data and other runtime dependencies
RUN apt-get update && apt-get install -y \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
ENV TZ=Asia/Tokyo

# Create non-root user
RUN useradd --create-home --shell /bin/bash fitlog

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=fitlog:fitlog /app/.venv /app/.venv

# Copy application code
COPY --chown=fitlog:fitlog fitlog/ ./fitlog/
COPY --chown=fitlog:fitlog scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p logs auth && chown -R fitlog:fitlog /app

# Switch to non-root user
USER fitlog

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["python", "-m", "fitlog.fetch", "--help"]