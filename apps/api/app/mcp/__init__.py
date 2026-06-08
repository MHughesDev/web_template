"""MCP (Model Context Protocol) server scaffold.

Mounts an MCP server over the FastAPI app's OpenAPI-derived tools. Controlled
by settings.MCP_ENABLED (off by default — see security note below).

Security default: deny-by-default, allowlist-by-tag. ``include_tags`` starts
empty so flipping MCP_ENABLED on does not silently turn the entire API
surface into AI-callable tools — add tags to the allowlist deliberately as
you decide which endpoints should be MCP tools (see
docs/procedures/add-mcp-tool.md §5.2.5). MCP calls are also auth-gated
through the same ``get_current_user`` dependency as regular API requests.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI
from fastapi_mcp import FastApiMCP
from fastapi_mcp.types import AuthConfig

from app.api.deps import get_current_user

# Hand-written MCP-only tools live on this router — register them here,
# before FastApiMCP is constructed, per docs/procedures/add-mcp-tool.md §5.2.6.
_mcp_custom_router = APIRouter()


def mount_mcp(app: FastAPI) -> None:
    app.include_router(_mcp_custom_router)

    mcp = FastApiMCP(
        app,
        name="template-mcp-server",
        description="MCP server exposing this app's allowlisted endpoints as AI-callable tools.",
        include_tags=[],
        auth_config=AuthConfig(dependencies=[Depends(get_current_user)]),
    )
    mcp.mount_http()
