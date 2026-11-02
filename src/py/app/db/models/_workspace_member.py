from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._workspace_roles import WorkspaceRoles

if TYPE_CHECKING:
    from app.db.models._workspace import Workspace
    from app.db.models._user import User


class WorkspaceMember(UUIDv7AuditBase):
    """Workspace Membership."""

    __tablename__ = "workspace_member"
    __table_args__ = (UniqueConstraint("user_id", "workspace_id"),)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_account.id", ondelete="cascade"), nullable=False)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspace.id", ondelete="cascade"), nullable=False)
    role: Mapped[WorkspaceRoles] = mapped_column(
        String(length=50),
        default=WorkspaceRoles.MEMBER,
        nullable=False,
        index=True,
    )
    is_owner: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped[User] = relationship(
        back_populates="workspaces",
        foreign_keys="WorkspaceMember.user_id",
        innerjoin=True,
        uselist=False,
        lazy="joined",
    )
    name: AssociationProxy[str] = association_proxy("user", "name")
    email: AssociationProxy[str] = association_proxy("user", "email")
    workspace: Mapped[Workspace] = relationship(
        back_populates="members",
        foreign_keys="WorkspaceMember.workspace_id",
        innerjoin=True,
        uselist=False,
        lazy="joined",
    )
    workspace_name: AssociationProxy[str] = association_proxy("workspace", "name")
