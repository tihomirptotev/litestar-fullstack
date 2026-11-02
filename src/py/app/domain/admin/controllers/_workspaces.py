"""Admin Workspaces Controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any
from uuid import UUID

from litestar import Controller, delete, get, patch
from litestar.di import Provide
from litestar.params import Dependency
from msgspec import UNSET
from sqlalchemy.orm import joinedload, selectinload

from app.db import models as m
from app.domain.accounts.guards import requires_superuser
from app.domain.admin.deps import provide_audit_log_service
from app.domain.admin.schemas import AdminWorkspaceDetail, AdminWorkspaceSummary, AdminWorkspaceUpdate
from app.domain.workspaces.services import WorkspaceService
from app.lib.deps import create_service_dependencies
from app.lib.schema import Message

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar import Request
    from litestar.security.jwt import Token

    from app.domain.admin.services import AuditLogService


class AdminWorkspacesController(Controller):
    """Admin workspace management endpoints."""

    tags = ["Admin"]
    path = "/api/admin/workspaces"
    guards = [requires_superuser]
    dependencies = create_service_dependencies(
        WorkspaceService,
        key="workspaces_service",
        load=[selectinload(m.Workspace.members).options(joinedload(m.WorkspaceMember.user, innerjoin=True))],
        error_messages={"duplicate_key": "This workspace already exists.", "integrity": "Workspace operation failed."},
        filters={
            "id_filter": UUID,
            "search": "name",
            "pagination_type": "limit_offset",
            "pagination_size": 25,
            "created_at": True,
            "updated_at": True,
            "sort_field": "created_at",
            "sort_order": "desc",
        },
    ) | {
        "audit_service": Provide(provide_audit_log_service),
    }

    @get(operation_id="AdminListWorkspaces", path="/")
    async def list_workspaces(
        self,
        workspaces_service: WorkspaceService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[AdminWorkspaceSummary]:
        """List all workspaces with pagination.

        Args:
            workspaces_service: Workspace service
            filters: Filter and pagination parameters

        Returns:
            Paginated workspace list
        """
        results, total = await workspaces_service.list_and_count(*filters)
        return workspaces_service.to_schema(results, total, filters, schema_type=AdminWorkspaceSummary)

    @get(operation_id="AdminGetWorkspace", path="/{workspace_id:uuid}")
    async def get_workspace(
        self,
        workspaces_service: WorkspaceService,
        workspace_id: UUID,
    ) -> AdminWorkspaceDetail:
        """Get detailed workspace information.

        Args:
            workspaces_service: Workspace service
            workspace_id: ID of workspace to retrieve

        Returns:
            Detailed workspace information
        """
        workspace = await workspaces_service.get(workspace_id)
        return workspaces_service.to_schema(workspace, schema_type=AdminWorkspaceDetail)

    @patch(operation_id="AdminUpdateWorkspace", path="/{workspace_id:uuid}")
    async def update_workspace(
        self,
        request: Request[m.User, Token, Any],
        workspaces_service: WorkspaceService,
        audit_service: AuditLogService,
        workspace_id: UUID,
        data: AdminWorkspaceUpdate,
    ) -> AdminWorkspaceDetail:
        """Update workspace as admin.

        Args:
            request: Request with authenticated superuser
            workspaces_service: Workspace service
            audit_service: Audit log service
            workspace_id: ID of workspace to update
            data: Update payload

        Returns:
            Updated workspace details
        """

        update_data: dict[str, Any] = {}
        for field in ("name", "description", "is_active"):
            value = getattr(data, field)
            if value is not UNSET:
                update_data[field] = value
        workspace = await workspaces_service.update(item_id=workspace_id, data=update_data, auto_commit=True)
        await audit_service.log_admin_workspace_update(
            actor_id=request.user.id,
            actor_email=request.user.email,
            workspace_id=workspace_id,
            workspace_name=workspace.name,
            changes=list(update_data.keys()),
            request=request,
        )
        return workspaces_service.to_schema(workspace, schema_type=AdminWorkspaceDetail)

    @delete(operation_id="AdminDeleteWorkspace", path="/{workspace_id:uuid}", status_code=200)
    async def delete_workspace(
        self,
        request: Request[m.User, Token, Any],
        workspaces_service: WorkspaceService,
        audit_service: AuditLogService,
        workspace_id: UUID,
    ) -> Message:
        """Delete a workspace (admin only).

        Args:
            request: Request with authenticated superuser
            workspaces_service: Workspace service
            audit_service: Audit log service
            workspace_id: ID of workspace to delete

        Returns:
            Success message
        """
        workspace = await workspaces_service.get(workspace_id)
        workspace_name = workspace.name
        await workspaces_service.delete(workspace.id)
        await audit_service.log_admin_workspace_delete(
            actor_id=request.user.id,
            actor_email=request.user.email,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            request=request,
        )
        return Message(message=f"Workspace {workspace_name} deleted successfully")
