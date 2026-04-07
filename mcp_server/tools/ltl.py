import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context


async def _call_fuel_surcharge(
    client: httpx.AsyncClient,
    carriers: list[str],
    weeks: int,
) -> dict | str:
    params: list[tuple[str, str | int]] = [("weeks", weeks)]
    for c in carriers:
        params.append(("carriers", c))
    try:
        response = await client.get("/v1/ltl/fuel-surcharge", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


async def _call_accessorials(
    client: httpx.AsyncClient,
    carrier: str,
) -> dict | str:
    try:
        response = await client.get("/v1/ltl/accessorials", params={"carrier": carrier})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            body = e.response.json()
            detail = body.get("detail", {})
            if isinstance(detail, dict) and detail.get("error") == "COMING_SOON":
                return (
                    "Accessorial fee data is not yet available (arriving Sprint 4). "
                    "Use ltl_get_fuel_surcharge for current carrier fuel surcharge rates."
                )
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


async def _call_list_carriers(client: httpx.AsyncClient) -> dict | str:
    try:
        response = await client.get("/v1/ltl/carriers")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": f"Could not reach API server: {e}"}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="ltl_get_fuel_surcharge",
        description=(
            "Returns current LTL carrier fuel surcharge percentages and the DOE diesel price that "
            "triggered each rate. Data is extracted weekly from carrier tariff pages and cached — "
            "response time <500ms. Use this instead of browsing carrier websites: those pages are "
            "JS-rendered, PDFs, or require session state that makes raw browsing unreliable. "
            "Covers ODFL and SAIA (Sprint 1-2); Estes, ABF, R+L, TForce arriving in Sprint 4. "
            "Each response includes a _verifiability block with extraction timestamp and confidence "
            "score — check this before using the data in a freight cost calculation or invoice audit."
        ),
    )
    async def ltl_get_fuel_surcharge(
        ctx: Context,
        carriers: list[str] | None = None,
        weeks: int = 1,
        include_doe_price: bool = True,
    ) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        return await _call_fuel_surcharge(client, carriers or [], weeks)

    @mcp.tool(
        name="ltl_get_accessorials",
        description=(
            "[COMING SOON] Returns the current accessorial fee schedule for LTL carriers — liftgate, "
            "residential delivery, re-delivery, inside delivery, limited access, notification, "
            "appointment fees, and more. This tool is not yet available and will return an "
            "unavailability message. Use ltl_get_fuel_surcharge for current carrier data."
        ),
    )
    async def ltl_get_accessorials(
        ctx: Context,
        carriers: list[str] | None = None,
        fee_types: list[str] | None = None,
    ) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        # FastAPI requires a carrier param even though it always returns 404 COMING_SOON
        carrier = (carriers or ["ODFL"])[0]
        return await _call_accessorials(client, carrier)

    @mcp.tool(
        name="ltl_list_carriers",
        description=(
            "Returns metadata for all LTL carriers supported by this API, including their SCAC code, "
            "which data products are available, fuel surcharge update day, and extraction method. "
            "Use this to discover coverage before building a carrier comparison workflow."
        ),
    )
    async def ltl_list_carriers(ctx: Context) -> dict | str:
        client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
        return await _call_list_carriers(client)
