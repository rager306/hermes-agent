# Honcho local Docker instance: base_url not read from host-level config

## Summary

When Honcho is configured at the **host level** (e.g., `hosts.hermes.baseUrl` in `honcho.json`), the `base_url` value is silently ignored. This causes `Invalid API key` errors and `Honcho init failed` warnings when using a local Docker Honcho instance that requires no API key, because the SDK defaults to the production cloud URL instead of the local one.

## Root Cause

In `honcho_integration/client.py`, the `HonchoClientConfig.from_global_config()` method resolves `base_url` like this:

```python
# BEFORE (broken):
base_url = (
    raw.get("baseUrl")                          # only root-level
    or os.environ.get("HONCHO_BASE_URL", "").strip()
    or None
)
```

It checks `raw.get("baseUrl")` (the top-level key in `honcho.json`) but **never checks** `host_block.get("baseUrl")` (the value nested under `hosts.hermes.baseUrl`). This means any `baseUrl` set at the host level is completely ignored.

## Config Structure That Fails

`~/.hermes/honcho.json`:
```json
{
  "hosts": {
    "hermes": {
      "apiKey": "eyJ...",
      "baseUrl": "http://127.0.0.1:8000",
      "workspace": "hermes",
      "enabled": true,
      ...
    }
  }
}
```

In this configuration:
- `apiKey` from `hosts.hermes` is correctly picked up (line 189-193)
- `workspace` from `hosts.hermes` is correctly picked up (line 177-180)
- **`baseUrl` from `hosts.hermes` is NOT picked up** — it falls through to `raw.get("baseUrl")` which is absent at root level, then to env var which is also absent → `base_url = None`
- With `base_url = None` AND `environment = "production"` (the default), the SDK tries to connect to `https://api.honcho.dev` with the local API key — causing `Invalid API key` error

## Fix

```python
# AFTER (fixed):
base_url = (
    host_block.get("baseUrl")   # <-- added: check host-level first
    or raw.get("baseUrl")
    or os.environ.get("HONCHO_BASE_URL", "").strip()
    or None
)
```

The `api_key` resolution was already correct (it checks `host_block` first), but `base_url` skipped the host-level check entirely.

## Impact

- **Symptoms**: `Invalid API key` error on startup, `Honcho init failed` warning printed to terminal
- **Affected**: Users who configure Honcho at the host level with `baseUrl` pointing to a local/self-hosted instance
- **Not affected**: Users who set `HONCHO_BASE_URL` env var, or who put `baseUrl` only at the root level of `honcho.json`

## Files Affected

- `honcho_integration/client.py` — `HonchoClientConfig.from_global_config()` method

## Test Case

```python
# Verify base_url is read from host block
cfg = HonchoClientConfig.from_global_config(host="hermes")
assert cfg.base_url == "http://127.0.0.1:8000"  # was None before fix
assert cfg.workspace_id == "hermes"
assert cfg.api_key == "eyJ..."  # already worked
```