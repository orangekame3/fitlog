# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev

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