# Codebase Structure

**Analysis Date:** 2026-03-26

## Directory Layout

```
hermes-agent/
├── run_agent.py           # AIAgent class — core conversation loop
├── model_tools.py         # Tool orchestration, discovery, dispatch
├── toolsets.py            # Toolset definitions and validation
├── cli.py                 # HermesCLI — interactive terminal interface
├── batch_runner.py        # Parallel batch processing
├── hermes_state.py        # SessionDB — SQLite session store with FTS5
├── hermes_time.py         # Timezone utilities
├── hermes_constants.py    # Constants including HERMES_HOME path
├── trajectory_compressor.py # Trajectory saving/compression
├── toolset_distributions.py # Tool distribution helpers
├── agent/                 # Agent internals package
├── tools/                 # Tool implementations package
├── gateway/               # Messaging platform gateway
├── hermes_cli/            # CLI subcommands and utilities
├── acp_adapter/           # ACP server (IDE integration)
├── cron/                  # Scheduled jobs
├── environments/          # RL training environments
├── honcho_integration/    # Honcho AI integration
├── tests/                 # Pytest test suite (~88 test files)
├── skills/                # Skill definitions and hub
├── website/               # Docusaurus documentation site
├── scripts/               # Utility scripts
├── acp_registry/          # ACP registry data
├── landingpage/           # Landing page assets
├── optional-skills/       # Optional skill implementations
└── .planning/             # GSD planning documents
```

## Directory Purposes

**`agent/` (Agent Internals):**
- Purpose: Core agent logic broken into focused modules
- Contains:
  - `prompt_builder.py` — System prompt assembly
  - `context_compressor.py` — Auto context compression
  - `prompt_caching.py` — Anthropic prompt caching
  - `auxiliary_client.py` — Auxiliary LLM client (vision, summarization)
  - `model_metadata.py` — Model context lengths, token estimation
  - `display.py` — KawaiiSpinner, tool preview formatting
  - `skill_commands.py` — Skill slash commands
  - `trajectory.py` — Trajectory saving helpers
  - `usage_pricing.py` — Cost estimation
  - `insights.py` — Usage insights

**`tools/` (Tool System):**
- Purpose: All tool implementations with self-registering registry
- Key files:
  - `registry.py` — Central `ToolRegistry` singleton (the base of the tool system)
  - `file_tools.py` — File read/write/search/patch
  - `web_tools.py` — Web search/extract
  - `terminal_tool.py` — Terminal orchestration
  - `browser_tool.py` — Browser automation
  - `mcp_tool.py` — MCP client
  - `delegate_tool.py` — Subagent delegation
  - `code_execution_tool.py` — Code execution sandbox
  - `memory_tool.py` — Memory/skill management
  - `skills_tool.py` — Skills hub integration
  - `send_message_tool.py` — Multi-platform messaging
  - `tts_tool.py`, `transcription_tools.py` — Voice features
  - `approval.py` — Dangerous command detection

**`gateway/` (Messaging Gateway):**
- Purpose: Bridge between agent and messaging platforms
- Key files:
  - `run.py` — `HermesGateway` main loop
  - `session.py` — `SessionStore` conversation persistence
  - `delivery.py` — Message delivery helpers
  - `platforms/` — Platform adapters

**`gateway/platforms/` (Platform Adapters):**
- Contains: `telegram.py`, `discord.py`, `slack.py`, `whatsapp.py`, `signal.py`, `sms.py`, `email.py`, `matrix.py`, `mattermost.py`, `dingtalk.py`, `homeassistant.py`, `webhook.py`, `api_server.py`

**`hermes_cli/` (CLI Subsystem):**
- Purpose: CLI utilities, commands, and configuration
- Key files:
  - `main.py` — Entry point for `hermes` command
  - `commands.py` — Slash command registry (`CommandDef`, `COMMAND_REGISTRY`)
  - `config.py` — `DEFAULT_CONFIG`, `OPTIONAL_ENV_VARS`
  - `auth.py` — Provider credential resolution
  - `banner.py` — ASCII art banner formatting
  - `skin_engine.py` — CLI skin/theme system
  - `setup.py` — Interactive setup wizard
  - `skills_config.py` — `hermes skills` command
  - `tools_config.py` — `hermes tools` command
  - `skills_hub.py` — Skills hub browser
  - `model_switch.py` — Model selection pipeline
  - `env_loader.py` — `.env` loading

**`acp_adapter/` (ACP Server):**
- Purpose: VS Code/Zed/JetBrains integration via Agent Client Protocol
- Key files: `server.py`, `session.py`, `tools.py`, `auth.py`, `permissions.py`, `events.py`

**`environments/` (RL Environments):**
- Purpose: Reinforcement learning environments for agent training
- Key files:
  - `hermes_base_env.py` — Base environment class
  - `agent_loop.py` — Main RL loop
  - `tool_context.py` — Tool execution context
  - `benchmarks/` — Benchmark environments (tblite, terminalbench2, yc_bench)
  - `tool_call_parsers/` — Model-specific tool call parsers

**`tests/` (Test Suite):**
- Purpose: Comprehensive pytest suite
- Structure:
  - `conftest.py` — Shared fixtures including `_isolate_hermes_home`
  - `test_run_agent.py` — Core agent tests
  - `test_model_tools.py` — Tool system tests
  - `test_cli_*.py` — CLI-specific tests
  - `gateway/`, `tools/`, `skills/` — Domain-specific tests

## Key File Locations

**Entry Points:**
- `run_agent.py` — AIAgent class, used by all modes
- `cli.py` — HermesCLI class, interactive terminal mode
- `gateway/run.py` — HermesGateway, messaging platform mode
- `acp_adapter/entry.py` — ACP server entry
- `batch_runner.py` — Batch processing entry

**Configuration:**
- `pyproject.toml` — Project metadata, dependencies, entry points
- `hermes_cli/config.py` — DEFAULT_CONFIG, OPTIONAL_ENV_VARS
- `cli-config.yaml.example` — Example config file

**Core Tool Files:**
- `tools/registry.py` — ToolRegistry singleton
- `model_tools.py` — Tool discovery and dispatch API
- `toolsets.py` — Toolset definitions

**State Management:**
- `hermes_state.py` — SessionDB SQLite store with FTS5
- `gateway/session.py` — Gateway session store

## Naming Conventions

**Files:**
- Python modules: `snake_case.py`
- Packages: `snake_case/` containing `__init__.py`
- Test files: `test_<module>.py` or `test_<feature>.py`

**Directories:**
- All `snake_case`

**Classes:**
- `PascalCase` (e.g., `AIAgent`, `HermesCLI`, `ToolRegistry`, `SessionStore`)

**Functions:**
- `snake_case` (e.g., `handle_function_call`, `get_tool_definitions`)

**Constants:**
- `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CONFIG`, `OPENROUTER_BASE_URL`)

**Modules/Packages:**
- `snake_case` throughout

## Where to Add New Code

**New Tool:**
1. Create `tools/my_tool.py`:
   ```python
   from tools.registry import registry

   def my_tool(param: str, task_id: str = None) -> str:
       return json.dumps({"success": True, "data": "..."})

   registry.register(
       name="my_tool",
       toolset="my_toolset",
       schema={...},
       handler=lambda args, **kw: my_tool(**kw),
   )
   ```
2. Import in `model_tools.py` `_discover_tools()`
3. Add to `toolsets.py` in appropriate toolset list

**New Slash Command:**
1. Add `CommandDef` to `hermes_cli/commands.py` `COMMAND_REGISTRY`
2. Add handler in `cli.py` `HermesCLI.process_command()`
3. If gateway-aware, add handler in `gateway/run.py`

**New Messaging Platform:**
1. Create `gateway/platforms/my_platform.py` extending `PlatformAdapter`
2. Implement required methods (`send_message`, `on_message`, etc.)
3. Register in `gateway/platforms/__init__.py`

**New RL Environment:**
1. Create `environments/my_env.py` extending `HermesBaseEnv`
2. Implement required abstract methods
3. Add to `environments/__init__.py`

## Special Directories

**`tests/`:**
- Purpose: All test code
- Generated: No
- Committed: Yes
- Note: `_isolate_hermes_home` fixture redirects `HERMES_HOME` to temp dir

**`skills/`:**
- Purpose: Skill definitions for skill hub
- Contains: JSON indexes of available skills

**`website/`:**
- Purpose: Docusaurus documentation site
- Generated: No (build artifacts are)
- Committed: Yes

**`.planning/`:**
- Purpose: GSD planning documents
- Generated: Yes (by this analysis)
- Committed: Yes

---

*Structure analysis: 2026-03-26*
