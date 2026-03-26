# Architecture

**Analysis Date:** 2026-03-26

## Pattern Overview

**Overall:** Layered Agent Architecture with Tool Registry Pattern

**Key Characteristics:**
- Central `ToolRegistry` singleton where all tools self-register at import time
- Clear separation between agent core (`run_agent.py`), CLI orchestration (`cli.py`), and tool implementations (`tools/`)
- OpenAI Chat Completions API compatible interface (messages format, tool_call format)
- Multi-platform messaging gateway with platform-specific adapters
- Reinforcement learning environment subsystem for agent training

## Layers

**Core Agent Layer:**
- Purpose: Main conversation loop, tool orchestration, message history management
- Location: `run_agent.py` (main entry), `agent/` package (internals)
- Contains: `AIAgent` class, prompt building, context compression, model metadata
- Depends on: `model_tools.py`, `agent/` modules
- Used by: CLI, gateway, batch runner, RL environments

**Tool System Layer:**
- Purpose: Tool registration, schema collection, handler dispatch
- Location: `tools/registry.py`, `tools/*.py`, `model_tools.py`
- Contains: `ToolRegistry` singleton, tool implementations
- Depends on: Nothing (registry is the base)
- Used by: `run_agent.py`, `cli.py`, `batch_runner.py`

**CLI Orchestration Layer:**
- Purpose: Interactive terminal interface with slash commands, autocomplete, skins
- Location: `cli.py`, `hermes_cli/` package
- Contains: `HermesCLI` class, slash command registry, setup wizards
- Depends on: `run_agent.py`, `agent/` modules, `hermes_cli/` modules
- Used by: End users via terminal

**Messaging Gateway Layer:**
- Purpose: Bridge between agent and messaging platforms (Slack, Discord, Telegram, etc.)
- Location: `gateway/run.py`, `gateway/platforms/`
- Contains: `HermesGateway` class, platform adapters
- Depends on: `run_agent.py` for agent execution
- Used by: Server deployment connecting to messaging platforms

**RL Training Layer:**
- Purpose: Reinforcement learning environments for agent improvement
- Location: `environments/` package, `agent_loop.py`
- Contains: `HermesBaseEnv`, `AgentLoop`, tool call parsers for different models
- Depends on: `run_agent.py`, `tools/`
- Used by: Training pipelines with Atropos/tinker

**ACP Adapter Layer:**
- Purpose: VS Code/Zed/JetBrains IDE integration via Agent Client Protocol
- Location: `acp_adapter/` package
- Contains: ACP server, session management, tool exposure
- Depends on: `agent/` modules
- Used by: IDE extensions

## Data Flow

**Interactive CLI Flow:**

```
User Input (terminal)
    → cli.py (HermesCLI.process_command() / chat input)
    → AIAgent.run_conversation() in run_agent.py
    → OpenAI-compatible API call (client.chat.completions.create)
    → handle_function_call() in model_tools.py
    → ToolRegistry.dispatch() → tool handler
    → Response returned through call stack
    → cli.py formats with KawaiiSpinner / rich panels
    → User sees output in terminal
```

**Tool Registration Flow:**

```
tools/*.py (import time)
    → ToolRegistry.register() calls
    → registry._tools{} populated
    ↓
model_tools.py (_discover_tools)
    → imports tools/registry and all tool files
    → triggers registration
    → get_tool_definitions() queries registry
    ↓
run_agent.py
    → passes tool schemas to API
    → receives tool_call responses
    → handle_function_call() dispatches to handlers
```

**Messaging Gateway Flow:**

```
Platform webhook (Slack/Telegram/etc.)
    → gateway/platforms/base.py (platform adapter)
    → gateway/run.py (HermesGateway.on_message())
    → run_agent.py (AIAgent.run_conversation())
    → Tool execution
    → gateway/delivery.py (send response to platform)
    → User receives message on platform
```

## Key Abstractions

**ToolRegistry (tools/registry.py):**
- Purpose: Central singleton for all tool registration and dispatch
- Examples: `tools/file_tools.py`, `tools/web_tools.py`, `tools/terminal_tool.py`
- Pattern: Each tool file calls `registry.register()` at module level with schema + handler

**AIAgent (run_agent.py):**
- Purpose: Core conversation loop with tool calling
- Examples: Used by CLI, gateway, batch_runner
- Pattern: `run_conversation()` loops calling API until non-tool response

**HermesCLI (cli.py):**
- Purpose: Interactive terminal interface
- Examples: `hermes` command entry point
- Pattern: Rich TUI with prompt_toolkit, slash command dispatch

**HermesGateway (gateway/run.py):**
- Purpose: Multi-platform message routing
- Examples: `gateway/platforms/telegram.py`, `gateway/platforms/discord.py`
- Pattern: Platform adapters normalize incoming/outgoing messages

**ToolCallParser (environments/tool_call_parsers/*.py):**
- Purpose: Parse tool calls from different model outputs
- Examples: `llama_parser.py`, `qwen_parser.py`, `deepseek_v3_parser.py`
- Pattern: Each model has its own output format for tool calls

## Entry Points

**CLI Entry:**
- Location: `cli.py`
- Triggers: `python cli.py` or `hermes` command
- Responsibilities: Interactive REPL, slash commands, tool/skill management

**Agent Entry:**
- Location: `run_agent.py`
- Triggers: `python run_agent.py` or `hermes-agent` command
- Responsibilities: Standalone agent execution, API proxy

**Gateway Entry:**
- Location: `gateway/run.py`
- Triggers: `python -m gateway` or `gateway` CLI
- Responsibilities: Long-running server for messaging platforms

**ACP Adapter Entry:**
- Location: `acp_adapter/entry.py`
- Triggers: `hermes-acp` command
- Responsibilities: IDE integration server

**Batch Runner Entry:**
- Location: `batch_runner.py`
- Triggers: `python batch_runner.py`
- Responsibilities: Parallel batch processing of tasks

## Error Handling

**Strategy:** Layered error handling with graceful degradation

**Patterns:**
- Tool handlers return `{"error": "..."}` JSON on failure (not exceptions)
- `ToolRegistry.dispatch()` catches all exceptions and returns error JSON
- API errors trigger retry logic with tenacity
- Context overflow errors trigger context compression
- Tool availability checks at startup and before tool use

## Cross-Cutting Concerns

**Logging:** Uses Python `logging` module with `logger = logging.getLogger(__name__)`

**Validation:** Pydantic for complex config, manual validation for simple cases

**Authentication:** Provider-specific credential resolution in `hermes_cli/auth.py`

**Environment:** `.env` loading via `hermes_cli/env_loader.py`, env vars override config file

---

*Architecture analysis: 2026-03-26*
