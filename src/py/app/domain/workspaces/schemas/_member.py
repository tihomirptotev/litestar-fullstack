"""Workspace member schemas."""

from uuid import UUID

from app.db.models._workspace_roles import WorkspaceRoles
from app.lib.schema import CamelizedBaseStruct


class WorkspaceMember(CamelizedBaseStruct):
    id: UUID
    user_id: UUID
    email: str
    name: str | None = None
    role: WorkspaceRoles | None = None
    is_owner: bool | None = False

    def __post_init__(self) -> None:
        """Set default role if not provided."""
        if self.role is None:
            self.role = WorkspaceRoles.MEMBER


class WorkspaceMemberModify(CamelizedBaseStruct):
    """Workspace Member Modify."""

    user_name: str


class WorkspaceMemberUpdate(CamelizedBaseStruct):
    """Workspace Member Update."""

    role: WorkspaceRoles
