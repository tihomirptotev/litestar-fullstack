"""Serve the built SPA frontend and static assets.

Replaces the serving behaviour previously provided by the ``litestar-vite``
plugin:

- a static files router mounted at ``/static/web`` (the app's ``STATIC_URL``)
  that serves everything from the app's ``STATIC_DIR`` (the output directory of
  ``vite build`` plus public assets checked into the repository), and
- an SPA fallback that serves ``index.html`` for any path not handled by an API
  route (e.g. ``/``, ``/auth/callback``, ``/dashboard``, ...).
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any

from litestar import Router
from litestar.connection import Request
from litestar.datastructures import CacheControlHeader
from litestar.enums import HttpMethod, MediaType
from litestar.exceptions import NotFoundException
from litestar.file_system import BaseLocalFileSystem
from litestar.handlers.http_handlers import HTTPRouteHandler
from litestar.response.file import ASGIFileResponse
from litestar.static_files import StaticFiles
from litestar.utils.path import normalize_path

if TYPE_CHECKING:
    from collections.abc import Sequence

    from litestar.types.composite_types import PathType

__all__ = ("create_spa_router",)


class SPAFiles(StaticFiles):
    """StaticFiles app that falls back to ``index.html`` for unmatched paths.

    Serves the SPA's ``index.html`` for client-side routes (e.g.
    ``/dashboard``) that have no matching file on disk, but still raises
    :class:`NotFoundException` for paths under ``asset_prefix`` so that missing
    build assets are reported as proper 404s instead of returning HTML.
    """

    __slots__ = ("asset_prefix", "index_html")

    def __init__(
        self,
        directories: Sequence[PathType],
        index_html: PathType,
        asset_prefix: str = "assets",
        resolve_symlinks: bool = True,
    ) -> None:
        """Initialize the SPA files app.

        Args:
            directories: Directories to serve files from.
            index_html: Absolute path to the built ``index.html``.
            asset_prefix: Path prefix, relative to the SPA mount, under which
                missing files must still return 404 (Vite's hashed bundle
                output lives under ``assets/``).
            resolve_symlinks: Resolve symlinks for the served directories.
        """
        super().__init__(
            is_html_mode=False,
            directories=directories,
            file_system=BaseLocalFileSystem(),
            send_as_attachment=False,
            resolve_symlinks=resolve_symlinks,
        )
        self.index_html = Path(index_html)
        self.asset_prefix = PurePosixPath(asset_prefix)

    async def get_index_response(self, is_head_response: bool) -> ASGIFileResponse:
        """Build the response that serves the SPA's ``index.html``.

        Args:
            is_head_response: Whether the response is a HEAD response.

        Returns:
            An ASGI file response for ``index.html``.

        Raises:
            NotFoundException: If ``index.html`` does not exist.
        """
        if not self.index_html.is_file():
            raise NotFoundException(f"SPA build not found: {self.index_html} does not exist") from None
        file_info = await self.adapter.info(self.index_html)
        return ASGIFileResponse(
            file_path=self.index_html,
            file_info=file_info,
            file_system=self.adapter.file_system,
            filename=self.index_html.name,
            content_disposition_type="inline",
            is_head_response=is_head_response,
        )

    async def handle(self, path: str, is_head_response: bool) -> ASGIFileResponse:
        """Resolve ``path`` to a file, falling back to ``index.html``.

        Args:
            path: The request path relative to the SPA mount.
            is_head_response: Whether the response is a HEAD response.

        Returns:
            The file response for the resolved file.

        Raises:
            NotFoundException: If the path is under ``asset_prefix`` and no
                file matches, or if ``index.html`` itself is missing.
        """
        try:
            return await super().handle(path=path, is_head_response=is_head_response)
        except NotFoundException:
            # Missing build assets (e.g. an old hashed bundle name) are plain 404s.
            parts = PurePosixPath("/" + path.strip("/")).parts[1:]
            if parts[: len(self.asset_prefix.parts)] == self.asset_prefix.parts:
                raise
            return await self.get_index_response(is_head_response=is_head_response)


def create_spa_router(
    path: str,
    directories: Sequence[PathType],
    index_html: PathType,
    name: str = "spa",
    cache_control: CacheControlHeader | None = None,
) -> Router:
    """Create a router that serves a single-page application.

    The router serves static files from ``directories`` and serves the built
    ``index.html`` for any path without a matching file. Missing files under
    the ``assets/`` prefix of the mount are not part of the SPA fallback and
    404 as usual.

    Args:
        path: The URL prefix under which the SPA is mounted (e.g. ``/``).
        directories: Directories to serve files from (the SPA bundle).
        index_html: Absolute path to the built ``index.html``.
        name: Name of the router.
        cache_control: Optional cache control header for served files.

    Returns:
        A router serving the SPA with an ``index.html`` fallback.
    """
    static_files = SPAFiles(directories=directories, index_html=index_html)

    async def serve_index(request: Request[Any, Any, Any]) -> ASGIFileResponse:
        """Serve ``index.html`` for the mount root (e.g. ``/``)."""
        return await static_files.get_index_response(is_head_response=request.method == "HEAD")

    async def serve_file(request: Request[Any, Any, Any], file_path: Path) -> ASGIFileResponse:
        """Serve a static file, falling back to ``index.html`` if missing."""
        return await static_files.handle(path=file_path.as_posix(), is_head_response=request.method == "HEAD")

    async def spa_index(request: Request[Any, Any, Any]) -> ASGIFileResponse:
        """Serve the SPA entry point."""
        return await serve_index(request)

    async def spa_file(request: Request[Any, Any, Any], file_path: Path) -> ASGIFileResponse:
        """Serve static files and SPA routes."""
        return await serve_file(request, file_path)

    index_handler = HTTPRouteHandler(
        path="/",
        http_method=[HttpMethod.GET, HttpMethod.HEAD],
        media_type=MediaType.HTML,
        include_in_schema=False,
        cache=cache_control,
        name=f"{name}-index",
    )(spa_index)

    file_handler = HTTPRouteHandler(
        path="/{file_path:path}",
        http_method=[HttpMethod.GET, HttpMethod.HEAD],
        media_type=MediaType.HTML,
        include_in_schema=False,
        cache=cache_control,
        name=f"{name}-file",
    )(spa_file)

    return Router(
        path=normalize_path(path),
        route_handlers=[index_handler, file_handler],
        cache_control=cache_control,
    )