from mcp.server.fastmcp import FastMCP

from mcp_server.client import app_lifespan
from mcp_server.prompts import register_ltl_prompts, register_abc_prompts
from mcp_server.tools import abc, ltl


def _make_ltl_mcp() -> FastMCP:
    instance = FastMCP(
        name="nexusfeed-ltl",
        instructions=(
            "Real-time LTL carrier fuel surcharge rates for freight and logistics workflows. "
            "Covers ODFL, Saia, Estes, ABF, R+L, and TForce — data extracted weekly from "
            "carrier tariff pages (JS-rendered, PDFs) and served as normalized JSON. "
            "All responses include a _verifiability block with extraction timestamp and confidence score."
        ),
        lifespan=app_lifespan,
        streamable_http_path="/",
    )
    ltl.register(instance)
    register_ltl_prompts(instance)
    return instance


def _make_abc_mcp() -> FastMCP:
    instance = FastMCP(
        name="nexusfeed-abc",
        instructions=(
            "Real-time US state ABC (Alcoholic Beverage Control) liquor license compliance records. "
            "Covers CA, TX, NY, and FL — data extracted from state portals (JS-rendered, CAPTCHAs) "
            "and served as normalized JSON. "
            "All responses include a _verifiability block with extraction timestamp and confidence score."
        ),
        lifespan=app_lifespan,
        streamable_http_path="/",
    )
    abc.register(instance)
    register_abc_prompts(instance)
    return instance


def _make_combined_mcp() -> FastMCP:
    """Full server — used for the FastAPI /mcp mount and the legacy nexusfeed-mcp entry point."""
    instance = FastMCP(
        name="nexusfeed-mcp",
        instructions=(
            "Real-time B2B data APIs for freight and alcohol compliance workflows. "
            "Provides LTL carrier fuel surcharge rates and state ABC liquor license status — "
            "data that is structurally inaccessible to raw LLM browsing. "
            "All responses include a _verifiability block with extraction timestamp and confidence score."
        ),
        lifespan=app_lifespan,
        streamable_http_path="/",
    )
    ltl.register(instance)
    abc.register(instance)
    register_ltl_prompts(instance)
    register_abc_prompts(instance)
    return instance


# Singleton used by api/main.py for the FastAPI /mcp mount.
mcp = _make_combined_mcp()


def run() -> None:
    """Entry point: nexusfeed-mcp (all tools)."""
    mcp.run(transport="stdio")


def run_ltl() -> None:
    """Entry point: nexusfeed-ltl (LTL tools only)."""
    _make_ltl_mcp().run(transport="stdio")


def run_abc() -> None:
    """Entry point: nexusfeed-abc (ABC tools only)."""
    _make_abc_mcp().run(transport="stdio")


def run_http(host: str = "0.0.0.0", port: int = 8001) -> None:
    """Run combined server as standalone Streamable HTTP (local testing only).
    In production, FastAPI mounts the MCP server at /mcp instead.
    """
    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    run()
