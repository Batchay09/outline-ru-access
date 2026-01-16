# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Outline RU Access — VPN service for accessing Russian websites from abroad. Uses Outline (Shadowsocks) protocol with a Telegram bot for automatic key distribution.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│   Outline API    │────▶│  Shadowbox      │
│  (Python)       │     │  (REST, HTTPS)   │     │  (Docker)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

- **Telegram Bot** (`bot/bot.py`): Handles user requests, creates access keys via Outline API, generates QR codes
- **Outline Server**: Shadowbox container managed by Outline's install script, provides Shadowsocks proxy
- **Outline API**: REST API at `https://<server>:<port>/<secret>` for key management

## Commands

### Bot Development
```bash
# Install dependencies locally
cd bot && pip install -r requirements.txt

# Run bot locally (requires .env)
python bot.py

# Build and run with Docker
cd bot && docker-compose up -d --build

# View logs
docker logs outline-bot -f

# Restart bot
docker restart outline-bot
```

### Server Management
```bash
# Install Outline server (on VPS)
./install.sh

# Check Outline containers
docker ps | grep -E "shadowbox|watchtower"

# View Outline logs
docker logs shadowbox

# Get API credentials
cat /opt/outline/access.txt
```

## Environment Variables

Bot requires these env vars (in `bot/.env`):
- `BOT_TOKEN` — Telegram bot token from @BotFather
- `ADMIN_ID` — Telegram user ID for admin access
- `OUTLINE_API_URL` — Full Outline API URL with secret (from `/opt/outline/access.txt`)

## Outline API Endpoints

The bot uses these Outline API endpoints:
- `GET /access-keys` — List all keys
- `POST /access-keys` — Create new key
- `DELETE /access-keys/{id}` — Delete key
- `PUT /access-keys/{id}/name` — Rename key

API uses self-signed certificate, requests made with `verify=False`.

## Bot Features

**User functions:**
- Get VPN access key with QR code
- Platform-specific installation instructions (iOS/Android/Windows/macOS)

**Admin functions** (only for `ADMIN_ID`):
- View statistics
- List all keys
- Create/delete keys manually
