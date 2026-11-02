"""Workspaces domain schemas."""

from app.domain.workspaces.schemas._invitation import WorkspaceInvitation, WorkspaceInvitationCreate
from app.domain.workspaces.schemas._member import WorkspaceMember, WorkspaceMemberModify, WorkspaceMemberUpdate
from app.domain.workspaces.schemas._workspace import Workspace, WorkspaceCreate, WorkspaceTag, WorkspaceUpdate
from app.lib.schema import Message

__all__ = (
    "Message",
    "Workspace",
    "WorkspaceCreate",
    "WorkspaceInvitation",
    "WorkspaceInvitationCreate",
    "WorkspaceMember",
    "WorkspaceMemberModify",
    "WorkspaceMemberUpdate",
    "WorkspaceTag",
    "WorkspaceUpdate",
)
