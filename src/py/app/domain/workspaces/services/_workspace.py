from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID  # noqa: TC003

from advanced_alchemy.exceptions import RepositoryError
from advanced_alchemy.extensions.litestar import repository, service

from app.db import models as m
from app.domain.tags.services import TagService
from app.lib import constants
from app.lib.deps import CompositeServiceMixin
from app.lib.service import AutoSlugServiceMixin

if TYPE_CHECKING:
    from advanced_alchemy.service import ModelDictT


class WorkspaceService(
    CompositeServiceMixin, AutoSlugServiceMixin[m.Workspace], service.SQLAlchemyAsyncRepositoryService[m.Workspace]
):
    """Handles CRUD operations on Workspace resources."""

    class Repo(repository.SQLAlchemyAsyncSlugRepository[m.Workspace]):
        """Workspace Repository."""

        model_type = m.Workspace

    repository_type = Repo
    match_fields = ["name"]

    @property
    def tags(self) -> TagService:
        """Lazy-loaded tag service sharing this session.

        Returns:
            The tag service instance.
        """
        return self._get_service(TagService)

    async def to_model_on_create(self, data: ModelDictT[m.Workspace]) -> ModelDictT[m.Workspace]:
        data = service.schema_dump(data)
        data = await self._populate_slug(data)
        return await self._populate_with_owner_and_tags(data, "create")

    async def to_model_on_update(self, data: ModelDictT[m.Workspace]) -> ModelDictT[m.Workspace]:
        data = service.schema_dump(data)
        data = await self._populate_slug(data)
        return await self._populate_with_owner_and_tags(data, "update")

    async def to_model_on_upsert(self, data: ModelDictT[m.Workspace]) -> ModelDictT[m.Workspace]:
        data = service.schema_dump(data)
        data = await self._populate_slug(data)
        return await self._populate_with_owner_and_tags(data, "upsert")

    @staticmethod
    def can_view_all(user: m.User) -> bool:
        return bool(
            user.is_superuser
            or any(
                assigned_role.role.name
                for assigned_role in user.roles
                if assigned_role.role.name == constants.SUPERUSER_ACCESS_ROLE
            ),
        )

    async def _populate_with_owner_and_tags(
        self,
        data: ModelDictT[m.Workspace],
        operation: str | None,
    ) -> ModelDictT[m.Workspace]:
        if not service.is_dict(data):
            return data

        owner_id: UUID | None = data.pop("owner_id", None)
        owner: m.User | None = data.pop("owner", None)
        input_tags: list[str] | None = data.pop("tags", None)
        if operation == "create" and owner_id is None and owner is None:
            msg = "'owner_id' is required to create a workspace."
            raise RepositoryError(msg)
        data = await super().to_model(data)
        if operation == "create":
            owner_data: dict[str, Any] = {"user": owner} if owner else {"user_id": owner_id}
            data.members.append(m.WorkspaceMember(**owner_data, role=m.WorkspaceRoles.ADMIN, is_owner=True))
        if input_tags is not None:
            data.tags = list(await self.tags.upsert_many([{"name": tag_text} for tag_text in input_tags]))
        return data

    async def update(self, data: ModelDictT[m.Workspace], item_id: Any | None = None, **kwargs: Any) -> m.Workspace:
        """Update workspace with owner change support.

        Handles owner changes by updating member records after the base update.

        Returns:
            The updated workspace object.
        """
        pending_owner_id: UUID | None = None
        if service.is_dict_with_field(data, "owner_id"):
            pending_owner_id = data.get("owner_id")
        workspace = await super().update(data, item_id=item_id, **kwargs)
        if pending_owner_id is not None:
            await self._transfer_ownership(workspace, pending_owner_id)
        return workspace

    async def _transfer_ownership(self, workspace: m.Workspace, new_owner_id: UUID) -> None:
        """Transfer workspace ownership to a new member."""
        await self.repository.session.refresh(workspace, ["members"])
        for member in workspace.members:
            if member.user_id == new_owner_id:
                member.is_owner = True
                member.role = m.WorkspaceRoles.ADMIN
            elif member.is_owner:
                member.is_owner = False
