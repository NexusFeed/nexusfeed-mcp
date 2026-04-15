# NexusFeed LTL — Claude Code Plugin

Real-time LTL freight carrier fuel surcharge rates for AI agents. 11 carriers (ODFL, Saia, Estes, ABF, R+L, TForce, XPO, SEFL, Averitt, FedEx, UPS) with a verifiable provenance block on every response.

## Install

```
/plugin marketplace add NexusFeed/nexusfeed-mcp
/plugin install nexusfeed-ltl@nexusfeed
```

## Auth

Set `MCP_API_KEY` in your environment to a NexusFeed API key. Get one at [nexusfeed.dev/signup](https://nexusfeed.dev/signup) (first 100 requests free).

```
export MCP_API_KEY=sk_live_...
```

`MCP_API_BASE_URL` defaults to `https://api.nexusfeed.dev` and usually does not need to be changed.

## Tools

- `get_fuel_surcharge` — current and historical fuel-surcharge rates for a carrier
- `list_carriers` — all 11 supported LTL carriers

Every response includes a `_verifiability` block with `extraction_confidence`, `source_timestamp`, `raw_data_evidence_url`, and `extraction_method` — see [docs.nexusfeed.dev/verifiability](https://docs.nexusfeed.dev/verifiability).

## Docs

Full reference: [docs.nexusfeed.dev/products/ltl-fuel-surcharge](https://docs.nexusfeed.dev/products/ltl-fuel-surcharge).
