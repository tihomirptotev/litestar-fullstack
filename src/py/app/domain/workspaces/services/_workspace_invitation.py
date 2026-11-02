from __future__ import annotations

from advanced_alchemy.extensions.litestar import repository, service

from app.db import models as m


class WorkspaceInvitationService(service.SQLAlchemyAsyncRepositoryService[m.WorkspaceInvitation]):
    """Workspace Invitation Service."""

    class Repo(repository.SQLAlchemyAsyncRepository[m.WorkspaceInvitation]):
        """Workspace Invitation Repository."""

        model_type = m.WorkspaceInvitation

    repository_type = Repo

    async def to_model_on_create(
        self, data: service.ModelDictT[m.WorkspaceInvitation]
    ) -> service.ModelDictT[m.WorkspaceInvitation]:
        data = service.schema_dump(data)
        return await self._populate_inviter(data)

    async def to_model_on_update(
        self, data: service.ModelDictT[m.WorkspaceInvitation]
    ) -> service.ModelDictT[m.WorkspaceInvitation]:
        data = service.schema_dump(data)
        return await self._populate_inviter(data)

    async def to_model_on_upsert(
        self, data: service.ModelDictT[m.WorkspaceInvitation]
    ) -> service.ModelDictT[m.WorkspaceInvitation]:
        data = service.schema_dump(data)
        return await self._populate_inviter(data)

    async def _populate_inviter(
        self, data: service.ModelDictT[m.WorkspaceInvitation]
    ) -> service.ModelDictT[m.WorkspaceInvitation]:
        if not service.is_dict(data):
            return data
        if (inviter := data.pop("invited_by", None)) is None:
            return data
        if service.is_dict_without_field(data, "invited_by_id"):
            data["invited_by_id"] = inviter.id
        if service.is_dict_without_field(data, "invited_by_email"):
            data["invited_by_email"] = inviter.email
        return data
