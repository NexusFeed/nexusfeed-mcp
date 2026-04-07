from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx

from mcp_server.config import settings


@dataclass
class AppContext:
    http_client: httpx.AsyncClient


@asynccontextmanager
async def app_lifespan(server):
    async with httpx.AsyncClient(
        base_url=settings.mcp_api_base_url,
        headers={"X-API-Key": settings.mcp_api_key},
        timeout=30.0,
    ) as client:
        yield AppContext(http_client=client)
