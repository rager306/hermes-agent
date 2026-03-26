# External Integrations

**Analysis Date:** 2026-03-26

## LLM Providers

**OpenRouter** (Primary - routes to multiple models)
- API Key: `OPENROUTER_API_KEY`
- Purpose: Access to Anthropic, OpenAI, Google, ZhipuAI, Moonshot, MiniMax models
- Used for: Main agent LLM calls, vision, web scraping helpers, MoA

**Anthropic**
- API Key: `ANTHROPIC_API_KEY` or `ANTHROPIC_TOKEN`
- Purpose: Direct Claude API access
- Used for: Primary model (claude-opus-4.6, claude-sonnet-4)

**Z.AI / GLM**
- API Key: `GLM_API_KEY` or `ZAI_API_KEY` or `Z_AI_API_KEY`
- Base URL: `GLM_BASE_URL` (optional override)
- Purpose: ZhipuAI GLM models (GLM-4-Plus)

**Kimi / Moonshot**
- API Key: `KIMI_API_KEY`
- Base URL: `KIMI_BASE_URL` (optional, defaults to api.kimi.com)
- Purpose: Moonshot AI coding models (kimi-k2.5)

**MiniMax**
- API Key: `MINIMAX_API_KEY` (international) or `MINIMAX_CN_API_KEY` (China)
- Base URL: `MINIMAX_BASE_URL` or `MINIMAX_CN_BASE_URL` (optional)
- Purpose: MiniMax models

**OpenCode Zen**
- API Key: `OPENCODE_ZEN_API_KEY`
- Base URL: `OPENCODE_ZEN_BASE_URL` (optional)
- Purpose: Curated tested models (GPT, Claude, Gemini, MiniMax, GLM, Kimi)

**OpenCode Go**
- API Key: `OPENCODE_GO_API_KEY`
- Base URL: `OPENCODE_GO_BASE_URL` (optional)
- Purpose: Open models subscription (GLM-5, Kimi K2.5, MiniMax M2.5)

**DeepSeek**
- API Key: `DEEPSEEK_API_KEY`
- Base URL: `DEEPSEEK_BASE_URL` (optional)
- Purpose: DeepSeek models

**DashScope (Alibaba)**
- API Key: `DASHSCOPE_API_KEY`
- Base URL: `DASHSCOPE_BASE_URL` (optional)
- Purpose: Qwen models

## Tool API Providers

**Parallel**
- API Key: `PARALLEL_API_KEY`
- Purpose: AI-native web search and extract

**Firecrawl**
- API Key: `FIRECRAWL_API_KEY`
- Base URL: `FIRECRAWL_API_URL` (optional, for self-hosted)
- Purpose: Web search, extract, and crawl

**Tavily**
- API Key: `TAVILY_API_KEY`
- Purpose: AI-native web search, extract, and crawl

**Browserbase**
- API Key: `BROWSERBASE_API_KEY`
- Project ID: `BROWSERBASE_PROJECT_ID`
- Purpose: Cloud browser execution for web automation
- Advanced Stealth: `BROWSERBASE_ADVANCED_STEALTH` (Scale Plan only)

**Browser Use**
- API Key: `BROWSER_USE_API_KEY`
- Purpose: Cloud browser automation

**FAL.ai**
- API Key: `FAL_KEY`
- Purpose: Image generation

**OpenAI (Voice Tools)**
- API Key: `VOICE_TOOLS_OPENAI_KEY`
- Purpose: Whisper transcription, OpenAI TTS voices

**ElevenLabs**
- API Key: `ELEVENLABS_API_KEY`
- Purpose: Premium text-to-speech voices

## Messaging Platforms

**Telegram**
- Bot Token: `TELEGRAM_BOT_TOKEN`
- Allowed Users: `TELEGRAM_ALLOWED_USERS`
- Home Channel: `TELEGRAM_HOME_CHANNEL`
- Implementation: `gateway/platforms/telegram.py`

**Discord**
- Bot Token: `DISCORD_BOT_TOKEN`
- Allowed Users: `DISCORD_ALLOWED_USERS`
- Home Channel: `DISCORD_HOME_CHANNEL`
- Settings: `DISCORD_REQUIRE_MENTION`, `DISCORD_FREE_RESPONSE_CHANNELS`, `DISCORD_AUTO_THREAD`
- Implementation: `gateway/platforms/discord.py`

**WhatsApp**
- Implementation: Baileys bridge (built-in)
- Enabled: `WHATSAPP_ENABLED`
- Allowed Users: `WHATSAPP_ALLOWED_USERS`
- Run command: `hermes whatsapp` to pair
- Implementation: `gateway/platforms/whatsapp.py`

**Slack**
- Bot Token: `SLACK_BOT_TOKEN`
- App Token: `SLACK_APP_TOKEN`
- Allowed Users: `SLACK_ALLOWED_USERS`
- Home Channel: `SLACK_HOME_CHANNEL`
- Implementation: `gateway/platforms/slack.py`

**Signal**
- HTTP URL: `SIGNAL_HTTP_URL`
- Account: `SIGNAL_ACCOUNT`
- Allowed Users: `SIGNAL_ALLOWED_USERS`, `SIGNAL_GROUP_ALLOWED_USERS`
- Home Channel: `SIGNAL_HOME_CHANNEL`
- Implementation: `gateway/platforms/signal.py`

**Mattermost**
- Token: `MATTERMOST_TOKEN`
- URL: `MATTERMOST_URL`
- Allowed Users: `MATTERMOST_ALLOWED_USERS`
- Home Channel: `MATTERMOST_HOME_CHANNEL`
- Implementation: `gateway/platforms/mattermost.py`

**Matrix**
- Access Token: `MATRIX_ACCESS_TOKEN`
- Password: `MATRIX_PASSWORD`
- Homeserver: `MATRIX_HOMESERVER`
- User ID: `MATRIX_USER_ID`
- Allowed Users: `MATRIX_ALLOWED_USERS`
- Encryption: `MATRIX_ENCRYPTION`
- Home Room: `MATRIX_HOME_ROOM`
- Implementation: `gateway/platforms/matrix.py`

**Email (IMAP/SMTP)**
- Address: `EMAIL_ADDRESS`
- Password: `EMAIL_PASSWORD`
- IMAP Host: `EMAIL_IMAP_HOST`
- IMAP Port: `EMAIL_IMAP_PORT`
- SMTP Host: `EMAIL_SMTP_HOST`
- SMTP Port: `EMAIL_SMTP_PORT`
- Poll Interval: `EMAIL_POLL_INTERVAL`
- Allowed Users: `EMAIL_ALLOWED_USERS`
- Home Address: `EMAIL_HOME_ADDRESS`
- Implementation: `gateway/platforms/email.py`

**SMS (Twilio)**
- Account SID: `TWILIO_ACCOUNT_SID`
- Auth Token: `TWILIO_AUTH_TOKEN`
- Home Channel: `SMS_HOME_CHANNEL`
- Implementation: `gateway/platforms/sms.py`

**DingTalk**
- Client ID: `DINGTALK_CLIENT_ID`
- Client Secret: `DINGTALK_CLIENT_SECRET`
- Implementation: `gateway/platforms/dingtalk.py`

## Home Assistant

- Token: `HASS_TOKEN`
- URL: `HASS_URL` (optional)
- Implementation: `gateway/platforms/homeassistant.py`

## RL Training

**Tinker API**
- API Key: `TINKER_API_KEY`
- Purpose: Reinforcement learning training service
- URL: `RL_API_URL` (default: http://localhost:8080)

**Weights & Biases**
- API Key: `WANDB_API_KEY`
- Purpose: Experiment tracking and metrics

## Skills Hub

**GitHub**
- Personal Access Token: `GITHUB_TOKEN`
- App ID: `GITHUB_APP_ID`
- Private Key: `GITHUB_APP_PRIVATE_KEY_PATH`
- Installation ID: `GITHUB_APP_INSTALLATION_ID`
- Purpose: Skill search/install/publish, higher rate limits, bot identity

## Honcho (Persistent Memory)

- API Key: `HONCHO_API_KEY`
- Base URL: `HONCHO_BASE_URL` (for self-hosted)
- Purpose: AI-native persistent user modeling across sessions
- Config: `~/.honcho/config.json`

## STT Providers

**Local (default)**
- faster-whisper - No API key needed
- Model: "base" (tiny, base, small, medium, large-v3)

**Groq**
- API Key: `GROQ_API_KEY`
- Purpose: Free Whisper transcription

**OpenAI**
- API Key: `VOICE_TOOLS_OPENAI_KEY`
- Model: whisper-1

## Data Storage

**Sessions:**
- Location: `~/.hermes/sessions/`
- Format: JSON trajectory files
- Naming: `logs/session_YYYYMMDD_HHMMSS_UUID.json`

**Local Storage:**
- Hermes home: `~/.hermes/`
- Subdirectories: `cron/`, `sessions/`, `logs/`, `memories/`

## CI/CD & Deployment

**GitHub Actions:**
- `deploy-site.yml` - Website deployment
- `docs-site-checks.yml` - Documentation checks
- `nix.yml` - Nix builds
- `supply-chain-audit.yml` - Dependency auditing
- `tests.yml` - Test execution

**NixOS:**
- Declarative configuration via `flake.nix`
- NixOS modules in `nix/nixosModules.nix`
- Managed mode detection via `HERMES_MANAGED` env var

## Environment Configuration

**Config file priority (highest to lowest):**
1. Environment variables
2. `~/.hermes/config.yaml` (primary user-facing config)
3. `~/.hermes/gateway.json` (legacy defaults)
4. Built-in defaults

**Secrets location:**
- `~/.hermes/.env` - All API keys and secrets
- File permissions: 0600 (owner read/write only)

**Config migration:**
- Version tracking via `_config_version` in config.yaml
- Auto-migration on startup

---

*Integration audit: 2026-03-26*
