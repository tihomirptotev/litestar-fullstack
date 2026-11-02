"""Workspace domain guards.

# @lat: [[domains#Workspaces]]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.exceptions import PermissionDeniedException

from app.db import models as m
from app.lib import constants

if TYPE_CHECKING:
    from typing import Any

    from litestar.connection import ASGIConnection
    from litestar.handlers.base import BaseRouteHandler
    from litestar.security.jwt import Token


def requires_workspace_membership(connection: ASGIConnection[Any, m.User, Token, Any], _: BaseRouteHandler) -> None:
    """Verify the connection user is a member of the workspace.

    Args:
        connection (ASGIConnection): Request/Connection object.
        _ (BaseRouteHandler): Route handler.

    Raises:
        PermissionDeniedException: Not authorized
    """
    workspace_id = connection.path_params["workspace_id"]
    has_system_role = any(
        assigned_role.role_name
        for assigned_role in connection.user.roles
        if assigned_role.role_name == constants.SUPERUSER_ACCESS_ROLE
    )
    has_workspace_role = any(membership.workspace.id == workspace_id for membership in connection.user.workspaces)
    if connection.user.is_superuser or has_system_role or has_workspace_role:
        return
    raise PermissionDeniedException(detail="Insufficient permissions to access workspace.")


def requires_workspace_admin(connection: ASGIConnection[Any, m.User, Token, Any], _: BaseRouteHandler) -> None:
    """Verify the connection user is a workspace admin.

    Args:
        connection (ASGIConnection): Request/Connection object.
        _ (BaseRouteHandler): Route handler.

    Raises:
        PermissionDeniedException: Not authorized
    """
    workspace_id = connection.path_params["workspace_id"]
    has_system_role = any(
        assigned_role.role_name
        for assigned_role in connection.user.roles
        if assigned_role.role_name == constants.SUPERUSER_ACCESS_ROLE
    )
    has_workspace_role = any(
        membership.workspace.id == workspace_id and membership.role == m.WorkspaceRoles.ADMIN for membership in connection.user.workspaces
    )
    if connection.user.is_superuser or has_system_role or has_workspace_role:
        return
    raise PermissionDeniedException(detail="Insufficient permissions to access workspace.")


def requires_workspace_ownership(connection: ASGIConnection[Any, m.User, Token, Any], _: BaseRouteHandler) -> None:
    """Verify that the connection user is the workspace owner.

    Args:
        connection (ASGIConnection): Request/Connection object.
        _ (BaseRouteHandler): Route handler.

    Raises:
        PermissionDeniedException: Not authorized
    """
    workspace_id = connection.path_params["workspace_id"]
    has_system_role = any(
        assigned_role.role_name
        for assigned_role in connection.user.roles
        if assigned_role.role_name == constants.SUPERUSER_ACCESS_ROLE
    )
    has_workspace_role = any(membership.workspace.id == workspace_id and membership.is_owner for membership in connection.user.workspaces)
    if connection.user.is_superuser or has_system_role or has_workspace_role:
        return

    msg = "Insufficient permissions to access workspace."
    raise PermissionDeniedException(msg)


__all__ = (
    "requires_workspace_admin",
    "requires_workspace_membership",
    "requires_workspace_ownership",
)
