# NexusFeed ABC — Claude Code Plugin

Liquor license compliance lookup across state Alcoholic Beverage Control portals for AI agents. Supports CA, NY, FL, TX, and IL — license status, expiration, owner, DBA, and address with a verifiable provenance block on every response.

## Install

```
/plugin marketplace add NexusFeed/nexusfeed-mcp
/plugin install nexusfeed-abc@nexusfeed
```

## Auth

Set `MCP_API_KEY` in your environment to a NexusFeed API key. Get one at [nexusfeed.dev/signup](https://nexusfeed.dev/signup) (first 100 requests free).

```
export MCP_API_KEY=sk_live_...
```

`MCP_API_BASE_URL` defaults to `https://api.nexusfeed.dev` and usually does not need to be changed.

## Tools

- `search_abc_license` — search by DBA name, owner, or address
- `lookup_abc_license` — direct lookup by license number

Every response includes a `_verifiability` block with `extraction_confidence`, `source_timestamp`, `raw_data_evidence_url`, and `extraction_method` — see [docs.nexusfeed.dev/verifiability](https://docs.nexusfeed.dev/verifiability).

## Docs

Full reference: [docs.nexusfeed.dev/products/abc-license-lookup](https://docs.nexusfeed.dev/products/abc-license-lookup).
