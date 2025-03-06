from typing import Callable, Optional, TypeVar, Union, overload

from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.types import Lifespan, Receive, Scope, Send

from open_tool_server import root
from open_tool_server._version import __version__
from open_tool_server.auth import Auth
from open_tool_server.auth.middleware import (
    ServerAuthenticationBackend,
    on_auth_error,
)
from open_tool_server.tools import InjectedRequest, ToolHandler, create_tools_router

T = TypeVar("T", bound=Callable)


class Server:
    """LangChain tool server."""

    def __init__(
        self, *, lifespan: Lifespan | None = None, enable_mcp: bool = False
    ) -> None:
        """Initialize the server."""
        self.app = FastAPI(version=__version__, lifespan=lifespan)
        # Routes that go under `/`
        self.app.include_router(root.router)
        # Create a tool handler
        self.tool_handler = ToolHandler()
        # Routes that go under `/tools`
        router = create_tools_router(self.tool_handler)
        self.app.include_router(router, prefix="/tools")

        self._auth = Auth()
        # Also create the tool handler.
        # For now, it's a global that's referenced by both MCP and /tools router
        # Routes that go under `/mcp` (Model Context Protocol)
        self._enable_mcp = enable_mcp

        if enable_mcp:
            from open_tool_server.mcp import MCP_APP_PREFIX, create_mcp_app

            self.app.mount(MCP_APP_PREFIX, create_mcp_app(self.tool_handler))

    @overload
    def tool(self, fn: T, *, permissions: list[str] | None = None) -> T: ...

    @overload
    def tool(self, *, permissions: list[str] | None = None) -> Callable[[T], T]: ...

    def tool(
        self,
        fn: Optional[T] = None,
        *,
        permissions: list[str] | None = None,
    ) -> Union[T, Callable[[T], T]]:
        """A decorator adds an existing function as a tool.

        Can be used both with and without parentheses:

        Example with parentheses:

            @app.tool()
            async def echo(msg: str) -> str:
                return msg + "!"

        Example without parentheses:

            @app.tool
            async def add(x: int, y: int) -> int:
                return x + y
        """

        def decorator(fn: T) -> T:
            self.tool_handler.add(fn, permissions=permissions)
            # Return the original. The decorator is only to register the tool.
            return fn

        if fn is not None:
            return decorator(fn)
        return decorator

    def add_auth(self, auth: Auth) -> None:
        """Add an authentication handler to the server."""
        if not isinstance(auth, Auth):
            raise TypeError(f"Expected an instance of Auth, got {type(auth)}")

        if self._auth._authenticate_handler is not None:
            raise ValueError(
                "Please add an authentication handler before adding another one."
            )

        # Make sure that the tool handler enables authentication checks.
        # Needed b/c Starlette's Request object raises assertion errors if
        # trying to access request.auth when auth is not enabled.
        self.tool_handler.auth_enabled = True

        if self._enable_mcp:
            raise AssertionError("MCPs Python SDK does not support authentication.")

        self.app.add_middleware(
            AuthenticationMiddleware,
            backend=ServerAuthenticationBackend(auth),
            on_error=on_auth_error,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI Application"""
        return await self.app.__call__(scope, receive, send)


__all__ = ["__version__", "Server", "Auth", "InjectedRequest"]
