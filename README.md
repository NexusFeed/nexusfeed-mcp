# nexusfeed-mcp

[![PyPI version](https://img.shields.io/pypi/v/nexusfeed-mcp)](https://pypi.org/project/nexusfeed-mcp/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Commercial](https://img.shields.io/badge/license-commercial-lightgrey.svg)](LICENSE)

Real-time LTL freight fuel surcharge rates and US state ABC liquor license compliance records — served as normalized, verifiable JSON for AI agents via the Model Context Protocol.

Data is extracted from carrier tariff pages and state ABC portals (JS-rendered, CAPTCHAs, session state) that are structurally inaccessible to raw LLM browsing. Every response includes a `_verifiability` block — extraction timestamp, confidence score, and source URL — so agents can assess data quality before acting.

## Tools

| Tool | Description |
|------|-------------|
| `ltl_get_fuel_surcharge` | Weekly fuel surcharge % for ODFL, Saia, Estes, ABF, R+L, TForce, XPO, SEFL, Averitt — DOE diesel price and up to 5 years of history |
| `ltl_list_carriers` | Carrier coverage metadata (SCAC codes, update schedule, extraction method) |
| `abc_search_licenses` | Search CA, TX, NY, FL license databases by trade name, owner, or address |
| `abc_lookup_license` | Point-in-time license status by state-issued license number |
| `abc_list_states` | State coverage, latency, and CAPTCHA requirements |

## Workflow Prompts

| Prompt | Description |
|--------|-------------|
| `freight_audit_workflow` | Multi-step LTL invoice audit against published carrier tariffs |
| `license_compliance_check` | Compliance verification before distributor orders, insurance binding, or merchant onboarding |

## Get API Access

Subscribe via RapidAPI to receive your `X-API-Key`. Freemium plans available (10 req/day free).

| Product | RapidAPI Listing |
|---------|-----------------|
| **LTL Fuel Surcharge** | [rapidapi.com/ladourv/api/ltl-fuel-surcharge-api](https://rapidapi.com/ladourv/api/ltl-fuel-surcharge-api) |
| **ABC License Compliance** | [rapidapi.com/ladourv/api/abc-license-compliance-api](https://rapidapi.com/ladourv/api/abc-license-compliance-api) |

## Install

```bash
pip install nexusfeed-mcp
# or with uv/uvx (no install needed):
uvx nexusfeed-mcp
```

## Configure

```bash
export MCP_API_BASE_URL=https://api.nexusfeed.dev
export MCP_API_KEY=sk_live_your_key_here
```

## Run (stdio)

```bash
# LTL tools only — 3 tools, 1 prompt
nexusfeed-ltl

# ABC tools only — 3 tools, 1 prompt
nexusfeed-abc

# All tools — 5 tools, 2 prompts
nexusfeed-mcp
```

## Claude Desktop Configuration

**LTL fuel surcharge only:**
```json
{
  "mcpServers": {
    "nexusfeed-ltl": {
      "command": "uvx",
      "args": ["--from", "nexusfeed-mcp", "nexusfeed-ltl"],
      "env": {
        "MCP_API_BASE_URL": "https://api.nexusfeed.dev",
        "MCP_API_KEY": "sk_live_your_key_here"
      }
    }
  }
}
```

**ABC license compliance only:**
```json
{
  "mcpServers": {
    "nexusfeed-abc": {
      "command": "uvx",
      "args": ["--from", "nexusfeed-mcp", "nexusfeed-abc"],
      "env": {
        "MCP_API_BASE_URL": "https://api.nexusfeed.dev",
        "MCP_API_KEY": "sk_live_your_key_here"
      }
    }
  }
}
```

**All tools:**
```json
{
  "mcpServers": {
    "nexusfeed-mcp": {
      "command": "uvx",
      "args": ["nexusfeed-mcp"],
      "env": {
        "MCP_API_BASE_URL": "https://api.nexusfeed.dev",
        "MCP_API_KEY": "sk_live_your_key_here"
      }
    }
  }
}
```

## Cline (VS Code) Configuration

Open Cline settings → MCP Servers → Add Server manually:

**LTL only:**
```json
{
  "nexusfeed-ltl": {
    "command": "uvx",
    "args": ["--from", "nexusfeed-mcp", "nexusfeed-ltl"],
    "env": {
      "MCP_API_BASE_URL": "https://api.nexusfeed.dev",
      "MCP_API_KEY": "sk_live_your_key_here"
    }
  }
}
```

**ABC only:**
```json
{
  "nexusfeed-abc": {
    "command": "uvx",
    "args": ["--from", "nexusfeed-mcp", "nexusfeed-abc"],
    "env": {
      "MCP_API_BASE_URL": "https://api.nexusfeed.dev",
      "MCP_API_KEY": "sk_live_your_key_here"
    }
  }
}
```

## Streamable HTTP (Smithery / remote clients)

| Server | URL |
|--------|-----|
| LTL tools | `https://api.nexusfeed.dev/mcp-ltl/` |
| ABC tools | `https://api.nexusfeed.dev/mcp-abc/` |

Pass your `X-API-Key` header on every request. Server metadata (no auth):
```
https://api.nexusfeed.dev/.well-known/mcp/server-card-ltl.json
https://api.nexusfeed.dev/.well-known/mcp/server-card-abc.json
```

## Verifiability

Every tool response includes:

```json
"_verifiability": {
  "source_timestamp": "2026-04-05T09:00:00Z",
  "extraction_confidence": 0.97,
  "raw_data_evidence_url": "https://odfl.com/...",
  "extraction_method": "api_mirror",
  "data_freshness_ttl_seconds": 604800
}
```

- `extraction_confidence >= 0.90` is required before using data in compliance-critical decisions
- `source_timestamp` within `data_freshness_ttl_seconds` means data is fresh from cache
- `raw_data_evidence_url` is the canonical source — agents can independently verify

## Example Usage

**Audit an LTL freight invoice:**
```
Use the freight_audit_workflow prompt with carrier="ODFL", invoice_date="2026-04-01",
invoiced_fuel_surcharge_pct="23.5" to check whether the billed rate matches the
published tariff.
```

**Verify a liquor license before a distributor transaction:**
```
Use abc_search_licenses with state="CA" and trade_name="Total Wine" to check
current license status, then abc_lookup_license for the full record with suspension history.
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 401 on every call | `MCP_API_KEY` is not set or is invalid |
| "Could not reach API server" | `MCP_API_BASE_URL` not set — should be `https://api.nexusfeed.dev` |
| TX endpoints return 503 | TX TABC requires 2Captcha configured server-side; use CA, NY, or FL instead |
| `extraction_confidence` < 0.90 | Data quality degraded — verify independently via `raw_data_evidence_url` |

## License

Commercial. See [LICENSE](LICENSE). Contact [ops@nexusfeed.dev](mailto:ops@nexusfeed.dev) for enterprise SLA and licensing.
