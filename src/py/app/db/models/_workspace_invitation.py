from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._workspace_roles import WorkspaceRoles

if TYPE_CHECKING:
    from app.db.models._workspace import Workspace
    from app.db.models._user import User


class WorkspaceInvitation(UUIDv7AuditBase):
    """Workspace Invite."""

    __tablename__ = "workspace_invitation"
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspace.id", ondelete="cascade"))
    email: Mapped[str] = mapped_column(index=True)
    role: Mapped[WorkspaceRoles] = mapped_column(String(length=50), default=WorkspaceRoles.MEMBER)
    is_accepted: Mapped[bool] = mapped_column(default=False)
    invited_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_account.id", ondelete="set null"))
    invited_by_email: Mapped[str]
    workspace: Mapped[Workspace] = relationship(foreign_keys="WorkspaceInvitation.workspace_id", innerjoin=True, viewonly=True)
    invited_by: Mapped[User | None] = relationship(
        foreign_keys="WorkspaceInvitation.invited_by_id", uselist=False, viewonly=True
    )
