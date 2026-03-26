# Technology Stack

**Analysis Date:** 2026-03-26

## Languages

**Primary:**
- Python 3.11+ - Core agent implementation, CLI, gateway, tools
- TypeScript/React 19 - Documentation website (Docusaurus)

**Secondary:**
- Nix - Package manager and deployment (flake-based)
- JavaScript - Minimal (website only)

## Runtime

**Python Environment:**
- Requires Python >= 3.11
- Uses `uv` for package management (not pip)
- Lockfile: `uv.lock` present

**Node Environment:**
- Node.js >= 18.0.0 (main project)
- Node.js >= 20.0.0 (website)

## Frameworks

**Core:**
- Pydantic 2.x - Data validation and settings management
- Python-dotenv 1.x - Environment variable loading
- Rich 14.x - Terminal UI and formatting
- Jinja2 3.x - Template rendering
- PyYAML 6.x - Configuration file parsing

**CLI:**
- Fire 0.7.x - CLI framework
- Prompt-toolkit 3.x - Interactive terminal prompts

**HTTP/Networking:**
- httpx 0.28.x - Async HTTP client
- requests 2.33.x - Synchronous HTTP (legacy)

**LLM Clients:**
- OpenAI 2.x - OpenAI API client
- Anthropic 0.39.x - Anthropic API client

**Retry/Resilience:**
- Tenacity 9.x - Retry logic

**Web Scraping/Tools:**
- Firecrawl-py 4.x - Web scraping and crawl
- parallel-web 0.4.x - Parallel web operations

**Voice/TTS:**
- edge-tts 7.x - Free Microsoft Edge TTS
- faster-whisper 1.x - Local Whisper transcription
- fal-client 0.13.x - Image generation API client

**Auth/Crypto:**
- PyJWT 2.x - JWT handling for GitHub App auth

**Optional Dependencies (extras):**
- Modal (swe-rex) - Cloud sandbox
- Daytona - Cloud sandbox
- python-telegram-bot 22.x - Telegram integration
- discord.py 2.x - Discord integration
- slack-bolt 1.x / slack-sdk 3.x - Slack integration
- matrix-nio 0.24.x - Matrix integration
- croniter 6.x - Cron scheduling
- FastAPI 0.104+ - API server
- uvicorn 0.24+ - ASGI server
- Weights & Biases (wandb) - Experiment tracking
- honcho-ai 2.x - Persistent memory
- MCP 1.2.x - Model Context Protocol
- dingtalk-stream 0.1.x - DingTalk integration
- aiohttp 3.13.x - Async HTTP (messaging platforms)

**Testing:**
- pytest 9.x - Test runner
- pytest-asyncio 1.x - Async test support
- pytest-xdist 3.x - Parallel test execution

**Website (Docusaurus):**
- Docusaurus 3.9.x - Documentation framework
- React 19.x - UI library
- TypeScript 5.6.x - Type safety

## Build System

**Python:**
- setuptools 61+ (build-backend)
- pyproject.toml as primary config

**Nix:**
- flake-parts - Flake composition
- pyproject-nix - Python package derivation
- uv2nix - UV to Nix integration

## Configuration

**Environment:**
- `.env.example` documents all environment variables
- `~/.hermes/config.yaml` - Primary user config
- `~/.hermes/.env` - API keys and secrets
- Config migration system with version tracking

**Key config files:**
- `pyproject.toml` - Python package definition
- `flake.nix` - Nix flake configuration
- `cli-config.yaml.example` - Example CLI configuration

**Config schemas:**
- Default config in `hermes_cli/config.py` (DEFAULT_CONFIG dict)
- Gateway config in `gateway/config.py` (GatewayConfig class)
- Platform enums: LOCAL, TELEGRAM, DISCORD, WHATSAPP, SLACK, SIGNAL, MATTERMOST, MATRIX, HOMEASSISTANT, EMAIL, SMS, DINGTALK, API_SERVER, WEBHOOK

## Platform Requirements

**Development:**
- Python 3.11+
- Node.js 18+ (for browser tools)
- UV package manager

**Production:**
- Supports multiple deployment methods:
  - Direct Python installation
  - Docker containers
  - Singularity containers
  - Modal cloud
  - Daytona cloud
  - SSH remote execution
  - NixOS (declarative)

**Terminal Sandboxes:**
- Local (direct execution)
- Docker (containerized)
- Singularity (containerized)
- Modal (serverless cloud)
- Daytona (cloud sandbox)
- SSH (remote execution)

---

*Stack analysis: 2026-03-26*
