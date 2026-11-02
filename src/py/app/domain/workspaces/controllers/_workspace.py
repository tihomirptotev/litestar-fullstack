"""Workspace Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar import Controller, delete, get, patch, post
from litestar.params import Dependency, Parameter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import models as m
from app.domain.workspaces.guards import requires_workspace_admin, requires_workspace_membership, requires_workspace_ownership
from app.domain.workspaces.schemas import Workspace, WorkspaceCreate, WorkspaceUpdate
from app.domain.workspaces.services import WorkspaceService
from app.lib.deps import create_service_dependencies

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service.pagination import OffsetPagination


class WorkspaceController(Controller):
    """Workspaces."""

    tags = ["Workspaces"]
    dependencies = create_service_dependencies(
        WorkspaceService,
        key="workspaces_service",
        load=[selectinload(m.Workspace.tags), selectinload(m.Workspace.members)],
        filters={
            "id_filter": UUID,
            "search": "name",
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "name",
            "sort_order": "asc",
        },
    )

    @get(component="workspace/list", operation_id="ListWorkspaces", path="/api/workspaces")
    async def list_workspaces(
        self,
        workspaces_service: WorkspaceService,
        current_user: m.User,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[Workspace]:
        """List workspaces that your account can access.

        Args:
            workspaces_service: Workspace Service
            current_user: Current User
            filters: Filters

        Returns:
            OffsetPagination[Workspace]
        """
        if not workspaces_service.can_view_all(current_user):
            results, total = await workspaces_service.list_and_count(
                *filters,
                m.Workspace.id.in_(
                    select(m.WorkspaceMember.workspace_id).where(m.WorkspaceMember.user_id == current_user.id).scalar_subquery()
                ),
            )
        else:
            results, total = await workspaces_service.list_and_count(*filters)
        return workspaces_service.to_schema(results, total, filters, schema_type=Workspace)

    @post(operation_id="CreateWorkspace", path="/api/workspaces")
    async def create_workspace(self, workspaces_service: WorkspaceService, current_user: m.User, data: WorkspaceCreate) -> Workspace:
        """Create a new workspace.

        Args:
            workspaces_service: Workspace Service
            current_user: Current User
            data: Workspace Create

        Returns:
            Workspace
        """
        obj = data.to_dict()
        obj.update({"owner_id": current_user.id, "owner": current_user})
        db_obj = await workspaces_service.create(obj)
        return workspaces_service.to_schema(db_obj, schema_type=Workspace)

    @get(operation_id="GetWorkspace", path="/api/workspaces/{workspace_id:uuid}", guards=[requires_workspace_membership])
    async def get_workspace(
        self,
        workspaces_service: WorkspaceService,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to retrieve.")],
    ) -> Workspace:
        """Get details about a workspace.

        Args:
            workspaces_service: Workspace Service
            workspace_id: Workspace ID

        Returns:
            Workspace
        """
        db_obj = await workspaces_service.get(workspace_id)
        return workspaces_service.to_schema(db_obj, schema_type=Workspace)

    @patch(operation_id="UpdateWorkspace", path="/api/workspaces/{workspace_id:uuid}", guards=[requires_workspace_admin])
    async def update_workspace(
        self,
        data: WorkspaceUpdate,
        workspaces_service: WorkspaceService,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to update.")],
    ) -> Workspace:
        """Update a workspace.

        Args:
            data: Workspace Update
            workspaces_service: Workspace Service
            workspace_id: Workspace ID

        Returns:
            Workspace
        """
        await workspaces_service.update(
            item_id=workspace_id,
            data=data.to_dict(),
        )

        fresh_obj = await workspaces_service.get_one(id=workspace_id)
        return workspaces_service.to_schema(fresh_obj, schema_type=Workspace)

    @delete(operation_id="DeleteWorkspace", path="/api/workspaces/{workspace_id:uuid}", guards=[requires_workspace_ownership])
    async def delete_workspace(
        self,
        workspaces_service: WorkspaceService,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to delete.")],
    ) -> None:
        """Delete a workspace.

        Args:
            workspaces_service: Workspace Service
            workspace_id: Workspace ID
        """
        _ = await workspaces_service.delete(workspace_id)
