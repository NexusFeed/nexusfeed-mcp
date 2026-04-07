from urllib.parse import quote

import httpx
from mcp.server.fastmcp import Context, FastMCP


async def _call_search_licenses(
    client: httpx.AsyncClient,
    state: str,
    dba_name: str | None,
    owner_name: str | None,
    address: str | None,
) -> dict | str:
    params: dict[str, str] = {"state": state}
    if dba_name:
        params["dba_name"] = dba_name
    if owner_name:
        params["owner_name"] = owner_name
    if address:
        params["address"] = address
    try:
        response = await client.get("/v1/abc/search", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


async def _call_lookup_license(
    client: httpx.AsyncClient,
    license_number: str,
    state: str,
) -> dict | str:
    encoded = quote(license_number, safe="")
    try:
        response = await client.get(f"/v1/abc/license/{encoded}", params={"state": state})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


async def _call_list_states(client: httpx.AsyncClient) -> dict | str:
    try:
        response = await client.get("/v1/abc/states")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="abc_search_licenses",
        description=(
            "Searches a US state ABC (Alcoholic Beverage Control) board database for liquor licenses "
            "matching a business name, owner name, or address. Returns license type, current status "
            "(ACTIVE / SUSPENDED / EXPIRED / REVOKED), expiration date, and any suspension history. "
            "Use this before approving a distributor order, binding an insurance policy, or onboarding "
            "a merchant to verify they hold a valid liquor license. Supports CA, TX, NY, and FL "
            "(TX requires TWOCAPTCHA_API_KEY configured server-side; NY uses NY Open Data API — active licenses only; "
            "FL searches the DBPR licensing portal across all board types). Always check the _verifiability block: "
            "extraction_confidence >= 0.90 and "
            "source_timestamp within data_freshness_ttl_seconds are required for compliance decisions. "
            "Note: city, county, zip, and license_status filters are accepted but not yet applied "
            "server-side — results may need post-filtering."
        ),
    )
    async def abc_search_licenses(
        ctx: Context,
        state: str,
        trade_name: str | None = None,
        owner_name: str | None = None,
        address: str | None = None,
        city: str | None = None,
        county: str | None = None,
        zip: str | None = None,
        license_status: list[str] | None = None,
        include_inactive: bool = False,
    ) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        # city, county, zip, license_status, include_inactive not yet forwarded (Sprint 4)
        return await _call_search_licenses(client, state, trade_name, owner_name, address)

    @mcp.tool(
        name="abc_lookup_license",
        description=(
            "Looks up a specific liquor license by its state-issued license number and returns the "
            "full current record including status, expiration, address, conditions, and suspension "
            "history. Faster and more precise than abc_search_licenses when you already have the "
            "license number. Use this for point-in-time verification (e.g., 'Is license CA-20-621547 "
            "currently ACTIVE?'). The _verifiability block contains the exact source URL — agents "
            "can independently verify the result by fetching that URL."
        ),
    )
    async def abc_lookup_license(
        ctx: Context,
        license_number: str,
        state: str,
    ) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        return await _call_lookup_license(client, license_number, state)

    @mcp.tool(
        name="abc_list_states",
        description=(
            "Returns metadata for all US states currently supported by the ABC License API, including "
            "the agency name, data freshness SLA, extraction method, and whether CAPTCHA is present. "
            "Use this first when building a multi-state compliance workflow to understand coverage."
        ),
    )
    async def abc_list_states(ctx: Context) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        return await _call_list_states(client)
