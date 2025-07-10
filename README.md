# fitlog

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A personal health data tracking system that fetches data from Google Fit API, stores it in InfluxDB, and visualizes it with Grafana. Designed to run on local machines (e.g., Raspberry Pi) with secure external access via Cloudflare Tunnel.

## Features

- **Data Collection**: Automatically fetch health data from Google Fit API
  - Step counts and daily activity
  - Body weight tracking
  - Sleep duration and patterns
  - Heart rate monitoring
  - Calorie consumption
- **Storage**: Time-series data storage with InfluxDB
- **Visualization**: Interactive dashboards with Grafana
- **Security**: OAuth 2.0 authentication with secure credential management
- **Automation**: Scheduled data collection with cron jobs
- **External Access**: Secure remote access via Cloudflare Tunnel
- **Demo Mode**: Mock data generation for testing and demonstration

## Architecture

### Production Mode
```
Google Fit API → Python Fetcher → InfluxDB (Docker) → Grafana (Docker) → Cloudflare Tunnel
```

### Demo Mode
```
Mock Data Generator → InfluxDB (Docker) → Grafana (Docker)
```

## Quick Start

### 🎬 Demo Mode (No Authentication Required)
```bash
# Clone the repository
git clone <repository-url>
cd fitlog

# Automated demo with continuous mock data generation
task demo

# Quick demo with immediate mock data
task demo-quick

# Access Grafana at http://localhost:3000
# Login: admin / fitlogdemo2024
```

### Option 1: Docker-only (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd fitlog

# Docker quick setup
task quickstart-docker

# Run data fetching in container
task docker-run-fetch-dry
```

### Option 2: Local development
```bash
# Clone the repository
git clone <repository-url>
cd fitlog

# Local quick setup (installs dependencies and starts services)
task quickstart

# View available tasks
task --list

# Get help
task help
```

## Prerequisites

- Docker & Docker Compose
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Task](https://taskfile.dev/) (task runner)
- Google Cloud Platform account

## Installation

1. **Project Setup**
   ```bash
   task setup
   ```

2. **Environment Configuration**
   ```bash
   # Create environment file
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Google Cloud Setup**
   - Create a new project in Google Cloud Console
   - Enable Google Fit API
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download credentials as `fitlog/auth/client_secret.json`

4. **Start Services**
   ```bash
   task docker-up
   ```

5. **Initial Authentication**
   ```bash
   task run-dry
   ```

## Usage

### Data Collection

#### Docker execution (Recommended)
```bash
# Fetch data (default: last 24 hours)
task docker-run-fetch

# Fetch data for specific days
task docker-run-fetch-days DAYS=7

# Dry run (no database writes)
task docker-run-fetch-dry
```

#### Mock data (for testing/demo)
```bash
# Generate mock health data
task mock

# Generate mock data for specific days
task mock DAYS=14

# Show mock data without writing to database
task mock-dry

# Generate mock data in Docker
task docker-mock
```

#### Local execution
```bash
# Fetch data (default: last 24 hours)
task run

# Fetch data for specific days
task run-days DAYS=7

# Dry run (no database writes)
task run-dry

# Test InfluxDB connection
task influx-test
```

### Development

```bash
# Format code
task fmt

# Run linting
task lint

# Run tests
task test

# Run tests with coverage
task test-cov
```

### Docker Management

#### Demo Environment
```bash
# Start demo services (automated mock data)
task demo-up

# Stop demo services
task demo-down

# View demo logs
task demo-logs

# Check demo status
task demo-status
```

#### Production Environment
```bash
# Start production services
task docker-up

# Stop production services
task docker-down

# Build fitlog image
task docker-build

# View production logs
task docker-logs

# Check production status
task docker-status

# Execute commands in production container
task docker-exec CMD="python --version"
```

### Monitoring

```bash
# View application logs
task logs

# View all logs
task logs-all

# Reset authentication
task auth-reset
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# InfluxDB Settings
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password
INFLUXDB_ORG=fitlog
INFLUXDB_BUCKET=health_data
INFLUXDB_ADMIN_TOKEN=your_admin_token

# Grafana Settings
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# Data Collection Settings
FETCH_DAYS_BACK=1
TIMEZONE=Asia/Tokyo
```

### OAuth Scopes

Required Google Fit API scopes:

- `https://www.googleapis.com/auth/fitness.activity.read`
- `https://www.googleapis.com/auth/fitness.body.read`
- `https://www.googleapis.com/auth/fitness.sleep.read`
- `https://www.googleapis.com/auth/fitness.heart_rate.read`

## Grafana Dashboard

Access Grafana at `http://localhost:3000`:

1. Login with admin credentials
2. Add InfluxDB as data source:
   - URL: `http://influxdb:8086`
   - Organization: `fitlog`
   - Token: Your admin token
   - Default bucket: `health_data`
3. Create dashboards for:
   - Daily step counts
   - Weight trends
   - Sleep patterns
   - Heart rate monitoring

## Automation

Set up automated data collection:

```bash
# Configure cron job
./scripts/setup_cron.sh

# Or manually add to crontab:
# 0 6 * * * /path/to/fitlog/scripts/run.sh
```

## External Access (Optional)

Configure Cloudflare Tunnel for remote access:

1. Install Cloudflare Tunnel
2. Configure `cloudflared/config.yml`
3. Run tunnel: `cloudflared tunnel run fitlog`

## Development Tools

This project uses modern Python development tools:

- **[uv](https://github.com/astral-sh/uv)**: Fast Python package manager
- **[Ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[Ty](https://github.com/astral-sh/ty)**: Fast type checker
- **[Task](https://taskfile.dev/)**: Task runner for development workflows

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `task test`
5. Run linting: `task lint`
6. Format code: `task fmt`
7. Submit a pull request

## Security

- Never commit authentication files (`client_secret.json`, `token.json`)
- Use strong passwords for database access
- Keep your environment variables secure
- Regularly rotate API tokens

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   task auth-reset
   task run-dry
   ```

2. **Database Connection Error**
   ```bash
   task docker-status
   task docker-logs
   ```

3. **No Data Retrieved**
   - Check Google Fit app has recorded data
   - Verify OAuth scopes are correct
   - Check API rate limits

### Logs

```bash
# View application logs
task logs

# View Docker logs
task docker-logs

# View all historical logs
task logs-all
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Create an issue on GitHub

## Acknowledgments

- Google Fit API for health data access
- InfluxDB for time-series data storage
- Grafana for data visualization
- Cloudflare for secure tunneling