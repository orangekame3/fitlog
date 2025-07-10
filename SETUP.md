# fitlog Setup Guide

Complete setup instructions for the Google Fit health data tracking system with InfluxDB and Grafana visualization.

### Quick Start

```bash
# Fully automated setup
task quickstart

# View available tasks
task --list

# Get help
task help
```

## Prerequisites

- Docker & Docker Compose
- Python 3.8+
- uv (Python package manager)
- Task (task runner)
- Google Cloud Platform account

## 1. Project Setup

```bash
# Clone repository
git clone <repository-url>
cd fitlog

# Project setup (recommended)
task setup

# Or manually with uv
uv sync --dev
```

## 2. Google Cloud Platform Configuration

### 2.1 Create Project and Enable APIs

1. Log in to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Google Fit API
   - Google People API (optional)

### 2.2 Create OAuth 2.0 Credentials

1. Navigate to "APIs & Services" → "Credentials" → "Create Credentials" → "OAuth client ID"
2. Application type: **Desktop Application**
3. Name: `fitlog-client` (or any name)
4. Download the JSON file after creation
5. Save as `fitlog/auth/client_secret.json`

## 3. Environment Configuration

```bash
# Create environment file
cp .env.example .env

# Edit environment file
nano .env
```

Configure required environment variables:

```env
# InfluxDB Settings
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password_here
INFLUXDB_ORG=fitlog
INFLUXDB_BUCKET=health_data
INFLUXDB_ADMIN_TOKEN=your_admin_token_here
INFLUXDB_URL=http://localhost:8086

# Grafana Settings
GRAFANA_ADMIN_PASSWORD=your_grafana_password_here

# Data Collection Settings
FETCH_DAYS_BACK=1
TIMEZONE=Asia/Tokyo
```

## 4. Start Docker Services

```bash
# Start InfluxDB and Grafana
task docker-up

# Check service status
task docker-status

# View logs
task docker-logs
```

## 5. Initial Authentication

```bash
# Initial run (OAuth authentication flow starts)
task run-dry

# Browser will open for Google authentication
# After authentication, token.json will be auto-generated
```

## 6. Data Collection Testing

```bash
# Test data collection
task run-days DAYS=7

# Regular execution
task run

# InfluxDB connection test
task influx-test

# Dry run (no database writes)
task run-dry
```

## 7. Automated Execution Setup

```bash
# Run cron setup script
./scripts/setup_cron.sh

# Or manually configure cron
crontab -e
# Add the following line:
# 0 6 * * * /path/to/fitlog/scripts/run.sh
```

## 8. Grafana Dashboard Configuration

1. Access `http://localhost:3000` in browser
2. Login with admin credentials (admin / password from .env)
3. Add InfluxDB as data source:
   - URL: `http://influxdb:8086`
   - Organization: `fitlog`
   - Token: Admin token from .env
   - Bucket: `health_data`

## 9. Cloudflare Tunnel Configuration (Optional)

For external access:

```bash
# Install Cloudflare Tunnel
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Create tunnel
cloudflared tunnel create fitlog

# Configure cloudflared/config.yml
# Start tunnel
cloudflared tunnel run fitlog
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify `client_secret.json` is in correct location
   - Check if APIs are enabled in Google Cloud Console

2. **InfluxDB Connection Error**
   - Verify Docker containers are running
   - Check .env configuration

3. **No Data Retrieved**
   - Ensure Google Fit app has recorded data
   - Verify OAuth scopes are correct

### Log Checking

```bash
# View application logs
task logs

# View all logs
task logs-all

# View Docker logs
task docker-logs
```

## Security Notes

- Never commit authentication files (`client_secret.json`, `token.json`)
- Manage .env file securely as it contains sensitive information
- Use strong passwords and tokens in production environments

## Support

If you encounter issues:

1. Check logs
2. Verify Docker container status
3. Review Google Cloud Console settings
4. Check environment variable configuration