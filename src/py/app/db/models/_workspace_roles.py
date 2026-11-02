from __future__ import annotations

from enum import StrEnum


class WorkspaceRoles(StrEnum):
    """Valid Values for Workspace Roles."""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
