# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fitlog is a personal health tracking system that fetches health data from Google Fit API, stores it in InfluxDB, and visualizes it with Grafana. It's designed to run on local machines (e.g., Raspberry Pi) with external access via Cloudflare Tunnel.

**Package Management**: This project uses `uv` for fast and reliable Python package management.

**Task Runner**: This project uses `task` (Taskfile) for development workflow automation.

## System Architecture

```
Google Fit API → Python Fetcher → InfluxDB (Docker) → Grafana (Docker) → Cloudflare Tunnel
```

### Key Components
- **fitlog/**: Main application code
  - `fetch.py`: Google Fit data fetching main script
  - `influx_writer.py`: InfluxDB write operations
  - `auth/`: OAuth 2.0 authentication files
    - `client_secret.json`: GCP console credentials (gitignored)
    - `token.json`: Auto-generated OAuth token (gitignored)
- **compose.yaml**: InfluxDB and Grafana container orchestration
- **cloudflared/config.yml**: Cloudflare Tunnel configuration
- **grafana/dashboards/**: Dashboard definitions (JSON)
- **scripts/run.sh**: Cron execution script

## Development Commands

### Docker Services
```bash
# Start InfluxDB and Grafana
task docker-up

# Stop services
task docker-down

# View logs
task docker-logs

# Check status
task docker-status
```

### Python Environment
```bash
# Install dependencies using uv
task setup

# Run main data fetcher
task run

# Run with custom days
task run-days DAYS=7

# Dry run (no database writes)
task run-dry

# Test InfluxDB connection
task influx-test
```

### Scheduling
```bash
# Add to crontab for automated data collection
0 6 * * * /path/to/fitlog/scripts/run.sh >> /var/log/fitlog.log 2>&1
```

## Google Fit API Integration

### Required OAuth Scopes
- `https://www.googleapis.com/auth/fitness.activity.read`
- `https://www.googleapis.com/auth/fitness.body.read`
- `https://www.googleapis.com/auth/fitness.sleep.read`
- `https://www.googleapis.com/auth/fitness.heart_rate.read`

## Available Tasks

View all available tasks:
```bash
task --list
```

Get help:
```bash
task help
```

### Main Development Tasks
- `task setup` - Initial project setup
- `task fmt` - Format code with Ruff
- `task lint` - Lint code with Ruff and Ty
- `task test` - Run tests
- `task run` - Execute data fetching
- `task docker-up` - Start Docker services

### Authentication Flow
1. Download `client_secret.json` from GCP Console
2. Place in `auth/` directory
3. First run generates `token.json` automatically
4. Both files are gitignored for security

## Data Pipeline

1. **Data Fetching**: `fetch.py` queries Google Fit API for specified time periods
2. **Data Processing**: JSON parsing and time series formatting
3. **Storage**: Write to InfluxDB via `influx_writer.py`
4. **Visualization**: Grafana dashboards consume InfluxDB data

## Security Considerations

- Never commit OAuth credentials (`client_secret.json`, `token.json`)
- Cloudflare Tunnel provides secure external access without port forwarding
- InfluxDB and Grafana run in isolated Docker containers

## Typical Data Types

- Step counts (24h/daily aggregation)
- Body weight trends
- Sleep duration heatmaps
- Calorie consumption (device-dependent)

## Development Tools

### Code Quality
```bash
# Format code
task fmt

# Lint code
task lint

# Run Ruff check
task ruff-check

# Run Ruff format
task ruff-format

# Type checking with Ty
task type-check
```

### Testing
```bash
# Run tests
task test

# Run tests with coverage
task test-cov

# Watch tests
task test-watch
```

### Quick Commands
```bash
# Pre-commit checks
task pre-commit

# CI pipeline
task ci

# Clean temporary files
task clean

# View logs
task logs

# Reset authentication
task auth-reset

# Quick start
task quickstart
```