from __future__ import annotations

from advanced_alchemy.base import orm_registry
from sqlalchemy import UUID, Column, ForeignKey, Table

workspace_tag = Table(
    "workspace_tag",
    orm_registry.metadata,
    Column("workspace_id", UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)
