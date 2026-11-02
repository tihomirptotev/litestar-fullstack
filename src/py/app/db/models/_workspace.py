from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDv7AuditBase

# @lat: [[domains#Database models]]
from advanced_alchemy.mixins import SlugKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._workspace_tag import workspace_tag

if TYPE_CHECKING:
    from app.db.models._tag import Tag
    from app.db.models._workspace_invitation import WorkspaceInvitation
    from app.db.models._workspace_member import WorkspaceMember


class Workspace(UUIDv7AuditBase, SlugKey):
    """A group of users with common permissions.
    Users can create and invite users to a workspace.
    """

    __tablename__ = "workspace"
    __pii_columns__ = {"name", "description"}
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(length=500), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="workspace",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )
    invitations: Mapped[list[WorkspaceInvitation]] = relationship(
        back_populates="workspace",
        cascade="all, delete",
    )
    pending_invitations: Mapped[list[WorkspaceInvitation]] = relationship(
        primaryjoin="and_(WorkspaceInvitation.workspace_id==Workspace.id, WorkspaceInvitation.is_accepted == False)",
        viewonly=True,
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=lambda: workspace_tag,
        back_populates="workspaces",
        cascade="all, delete",
        passive_deletes=True,
    )
