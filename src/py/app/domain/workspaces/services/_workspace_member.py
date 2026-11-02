from __future__ import annotations

from advanced_alchemy.extensions.litestar import repository, service

from app.db import models as m


class WorkspaceMemberService(service.SQLAlchemyAsyncRepositoryService[m.WorkspaceMember]):
    """Workspace Member Service."""

    class Repo(repository.SQLAlchemyAsyncRepository[m.WorkspaceMember]):
        """Workspace Member Repository."""

        model_type = m.WorkspaceMember

    repository_type = Repo
