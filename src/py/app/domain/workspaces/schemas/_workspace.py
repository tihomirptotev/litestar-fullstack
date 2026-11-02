"""Workspace schemas."""

from uuid import UUID

import msgspec

from app.domain.workspaces.schemas._member import WorkspaceMember
from app.lib.schema import CamelizedBaseStruct


class WorkspaceTag(CamelizedBaseStruct):
    id: UUID
    slug: str
    name: str


class Workspace(CamelizedBaseStruct):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True
    members: list[WorkspaceMember] = []
    tags: list[WorkspaceTag] = []


class WorkspaceCreate(CamelizedBaseStruct):
    name: str
    description: str | None = None
    tags: list[str] = []


class WorkspaceUpdate(CamelizedBaseStruct, omit_defaults=True):
    name: str | msgspec.UnsetType | None = msgspec.UNSET
    description: str | msgspec.UnsetType | None = msgspec.UNSET
    tags: list[str] | msgspec.UnsetType | None = msgspec.UNSET
