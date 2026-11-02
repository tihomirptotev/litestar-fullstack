"""Workspace Member Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, delete, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from litestar.status_codes import HTTP_202_ACCEPTED

from app.db import models as m
from app.domain.accounts.deps import provide_users_service
from app.domain.workspaces.deps import provide_workspace_members_service, provide_workspaces_service
from app.domain.workspaces.schemas import Workspace, WorkspaceMember, WorkspaceMemberModify, WorkspaceMemberUpdate

if TYPE_CHECKING:
    from uuid import UUID

    from app.domain.accounts.services import UserService
    from app.domain.workspaces.services import WorkspaceMemberService, WorkspaceService


class WorkspaceMemberController(Controller):
    """Workspace Members."""

    tags = ["Workspace Members"]
    dependencies = {
        "workspaces_service": Provide(provide_workspaces_service),
        "workspace_members_service": Provide(provide_workspace_members_service),
        "users_service": Provide(provide_users_service),
    }

    @post(operation_id="AddMemberToWorkspace", path="/api/workspaces/{workspace_id:uuid}/members")
    async def add_member_to_workspace(
        self,
        workspaces_service: WorkspaceService,
        workspace_members_service: WorkspaceMemberService,
        users_service: UserService,
        data: WorkspaceMemberModify,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to update.")],
    ) -> Workspace:
        """Add a member to a workspace.

        Args:
            workspaces_service: Workspace Service
            workspace_members_service: Workspace Member Service
            users_service: User Service
            data: Workspace Member Modify
            workspace_id: Workspace ID

        Raises:
            IntegrityError: If the user is already a member of the workspace.

        Returns:
            Workspace
        """
        user_obj = await users_service.get_one(email=data.user_name)
        existing_membership = await workspace_members_service.get_one_or_none(workspace_id=workspace_id, user_id=user_obj.id)
        if existing_membership is not None:
            msg = "User is already a member of the workspace."
            raise IntegrityError(msg)
        await workspace_members_service.create(
            {
                "workspace_id": workspace_id,
                "user_id": user_obj.id,
                "role": m.WorkspaceRoles.MEMBER,
                "is_owner": False,
            }
        )
        workspace_obj = await workspaces_service.get(workspace_id)
        return workspaces_service.to_schema(workspace_obj, schema_type=Workspace)

    @delete(
        operation_id="RemoveMemberFromWorkspace", path="/api/workspaces/{workspace_id:uuid}/members", status_code=HTTP_202_ACCEPTED
    )
    async def remove_member_from_workspace(
        self,
        workspaces_service: WorkspaceService,
        workspace_members_service: WorkspaceMemberService,
        users_service: UserService,
        data: WorkspaceMemberModify,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to delete.")],
    ) -> Workspace:
        """Revoke a member's access to a workspace.

        Args:
            workspaces_service: Workspace Service
            workspace_members_service: Workspace Member Service
            users_service: User Service
            data: Workspace Member Modify
            workspace_id: Workspace ID

        Raises:
            IntegrityError: If the user is not a member of the workspace.

        Returns:
            Workspace
        """
        user_obj = await users_service.get_one(email=data.user_name)
        membership = await workspace_members_service.get_one_or_none(workspace_id=workspace_id, user_id=user_obj.id)
        if membership is None:
            msg = "User is not a member of this workspace."
            raise IntegrityError(msg)
        await workspace_members_service.delete(membership.id)
        workspace_obj = await workspaces_service.get(workspace_id)
        return workspaces_service.to_schema(workspace_obj, schema_type=Workspace)

    @patch(operation_id="UpdateWorkspaceMember", path="/api/workspaces/{workspace_id:uuid}/members/{user_id:uuid}")
    async def update_workspace_member(
        self,
        workspace_members_service: WorkspaceMemberService,
        workspace_id: Annotated[UUID, Parameter(title="Workspace ID", description="The workspace to update.")],
        user_id: Annotated[UUID, Parameter(title="User ID", description="The user to update.")],
        data: WorkspaceMemberUpdate,
    ) -> WorkspaceMember:
        """Update a workspace member's role.

        Raises:
            IntegrityError: If the user is not a member of the workspace.

        Returns:
            The updated workspace member.
        """
        membership = await workspace_members_service.get_one_or_none(workspace_id=workspace_id, user_id=user_id)
        if membership is None:
            msg = "User is not a member of this workspace."
            raise IntegrityError(msg)
        updated = await workspace_members_service.update(item_id=membership.id, data={"role": data.role})
        return workspace_members_service.to_schema(updated, schema_type=WorkspaceMember)
