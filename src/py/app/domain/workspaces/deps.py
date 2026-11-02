"""Workspace domain dependencies."""

from __future__ import annotations

from sqlalchemy.orm import selectinload

from app.db import models as m
from app.domain.workspaces.services import WorkspaceInvitationService, WorkspaceMemberService, WorkspaceService
from app.lib.deps import create_service_provider

provide_workspaces_service = create_service_provider(
    WorkspaceService,
    load=[m.Workspace.tags, m.Workspace.members],
    error_messages={"duplicate_key": "This workspace already exists.", "integrity": "Workspace operation failed."},
)

provide_workspace_invitations_service = create_service_provider(
    WorkspaceInvitationService,
    load=[selectinload(m.WorkspaceInvitation.workspace)],
    error_messages={"duplicate_key": "Invitation already exists.", "integrity": "Workspace invitation operation failed."},
)

provide_workspace_members_service = create_service_provider(
    WorkspaceMemberService,
    load=[
        selectinload(m.WorkspaceMember.workspace),
        selectinload(m.WorkspaceMember.user),
    ],
    error_messages={"duplicate_key": "User is already a workspace member.", "integrity": "Workspace member operation failed."},
)

__all__ = (
    "provide_workspace_invitations_service",
    "provide_workspace_members_service",
    "provide_workspaces_service",
)
