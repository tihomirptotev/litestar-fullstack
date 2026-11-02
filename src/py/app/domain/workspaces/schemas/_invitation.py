"""Workspace invitation schemas."""

from datetime import datetime
from uuid import UUID

from app.db.models._workspace_roles import WorkspaceRoles
from app.lib.schema import CamelizedBaseStruct


class WorkspaceInvitationCreate(CamelizedBaseStruct):
    email: str
    role: WorkspaceRoles


class WorkspaceInvitation(CamelizedBaseStruct):
    id: UUID
    email: str
    role: WorkspaceRoles
    created_at: datetime
    updated_at: datetime
    is_accepted: bool = False
