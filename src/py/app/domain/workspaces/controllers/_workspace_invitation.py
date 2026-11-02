"""Workspace Invitation Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from litestar import Controller, Request, delete, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from sqlalchemy.orm import selectinload

from app.db import models as m
from app.domain.workspaces.deps import provide_workspace_members_service, provide_workspaces_service
from app.domain.workspaces.schemas import WorkspaceInvitation, WorkspaceInvitationCreate
from app.domain.workspaces.services import WorkspaceInvitationService
from app.lib.deps import create_service_dependencies
from app.lib.schema import Message

if TYPE_CHECKING:
    from uuid import UUID

    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination
    from litestar.security.jwt import Token

    from app.domain.workspaces.services import WorkspaceMemberService, WorkspaceService
    from app.lib.email import AppEmailService


class WorkspaceInvitationController(Controller):
    """Workspace Invitations."""

    path = "/api/workspaces/{workspace_id:uuid}/invitations"
    tags = ["Workspaces"]
    dependencies = create_service_dependencies(
        WorkspaceInvitationService,
        key="workspace_invitations_service",
        load=[selectinload(m.WorkspaceInvitation.workspace)],
        error_messages={
            "duplicate_key": "Invitation already exists.",
            "integrity": "Workspace invitation operation failed.",
        },
        filters={
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "created_at",
            "sort_order": "desc",
        },
    ) | {
        "workspaces_service": Provide(provide_workspaces_service),
        "workspace_members_service": Provide(provide_workspace_members_service),
    }

    @post(operation_id="CreateWorkspaceInvitation", path="")
    async def create_workspace_invitation(
        self,
        current_user: m.User,
        workspace_invitations_service: WorkspaceInvitationService,
        workspaces_service: WorkspaceService,
        app_mailer: AppEmailService,
        request: Request[m.User, Token, Any],
        workspace_id: UUID,
        data: WorkspaceInvitationCreate,
    ) -> WorkspaceInvitation:
        """Create a new workspace invitation.

        Args:
            current_user: The current user sending the invitation.
            workspace_invitations_service: The workspace invitation service.
            workspaces_service: The workspaces service.
            app_mailer: Email service for sending notifications.
            request: The request object.
            workspace_id: The workspace id.
            data: The data to create the workspace invitation with.

        Raises:
            HTTPException: If the invitee is already a workspace member

        Returns:
            The created workspace invitation.
        """
        workspace = await workspaces_service.get(workspace_id)
        if any(member.email == data.email for member in workspace.members):
            raise HTTPException(status_code=400, detail="User is already a member of this workspace")
        payload = data.to_dict()
        payload["workspace_id"] = workspace_id
        payload["invited_by"] = current_user
        db_obj = await workspace_invitations_service.create(payload)
        request.app.emit(event_id="workspace_invitation_created", invitation_id=db_obj.id, mailer=app_mailer)
        return workspace_invitations_service.to_schema(db_obj, schema_type=WorkspaceInvitation)

    @get(operation_id="ListWorkspaceInvitations", path="")
    async def list_workspace_invitations(
        self,
        workspace_invitations_service: WorkspaceInvitationService,
        workspace_id: UUID,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[WorkspaceInvitation]:
        """List workspace invitations.

        Args:
            workspace_id: The ID of the workspace to list the invitations for.
            workspace_invitations_service: The workspace invitation service.
            filters: Filter and pagination parameters

        Returns:
            The list of workspace invitations.
        """
        db_objs, total = await workspace_invitations_service.list_and_count(*filters, m.WorkspaceInvitation.workspace_id == workspace_id)
        return workspace_invitations_service.to_schema(db_objs, total, filters, schema_type=WorkspaceInvitation)

    @delete(operation_id="DeleteWorkspaceInvitation", path="/{invitation_id:uuid}")
    async def delete_workspace_invitation(
        self, workspace_invitations_service: WorkspaceInvitationService, workspace_id: UUID, invitation_id: UUID
    ) -> None:
        """Delete an invitation.

        Args:
            workspace_id: The ID of the workspace to delete the invitation for.
            invitation_id: The ID of the invitation to delete.
            workspace_invitations_service: The workspace invitation service.

        Raises:
            HTTPException: If the invitation does not belong to the workspace
        """
        invitation = await workspace_invitations_service.get(invitation_id)
        if invitation.workspace_id != workspace_id:
            raise HTTPException(status_code=400, detail="Invitation does not belong to this workspace")
        await workspace_invitations_service.delete(item_id=invitation_id)

    @post(operation_id="AcceptWorkspaceInvitation", path="/{invitation_id:uuid}/accept")
    async def accept_workspace_invitation(
        self,
        current_user: m.User,
        workspace_invitations_service: WorkspaceInvitationService,
        workspace_members_service: WorkspaceMemberService,
        workspace_id: UUID,
        invitation_id: UUID,
    ) -> Message:
        """Accept an invitation.

        Args:
            workspace_id: The ID of the workspace to accept the invitation for.
            invitation_id: The ID of the invitation to accept.
            workspace_invitations_service: The workspace invitation service.
            workspace_members_service: The workspace member service.
            current_user: The current user.

        Raises:
            HTTPException: If the invitation is invalid or the user cannot accept it

        Returns:
            A message indicating that the workspace invitation has been accepted.
        """
        db_obj = await workspace_invitations_service.get(item_id=invitation_id)
        if db_obj.workspace_id != workspace_id:
            raise HTTPException(status_code=400, detail="Invitation does not belong to this workspace")
        if db_obj.is_accepted:
            raise HTTPException(status_code=400, detail="Invitation has already been accepted")
        if db_obj.email != current_user.email:
            raise HTTPException(status_code=400, detail="You are not authorized to accept this invitation")
        existing_membership = await workspace_members_service.get_one_or_none(
            workspace_id=workspace_id,
            user_id=current_user.id,
        )
        if existing_membership is not None:
            raise HTTPException(status_code=400, detail="User is already a member of this workspace")
        _ = await workspace_members_service.create(
            {
                "workspace_id": workspace_id,
                "user_id": current_user.id,
                "role": db_obj.role,
                "is_owner": False,
            }
        )
        await workspace_invitations_service.update(item_id=invitation_id, data={"is_accepted": True})
        return Message(message="Workspace invitation accepted")

    @post(operation_id="RejectWorkspaceInvitation", path="/{invitation_id:uuid}/reject")
    async def reject_workspace_invitation(
        self,
        current_user: m.User,
        workspace_invitations_service: WorkspaceInvitationService,
        workspace_id: UUID,
        invitation_id: UUID,
    ) -> Message:
        """Reject an invitation.

        Raises:
            HTTPException: If the invitation is invalid or the user cannot reject it

        Returns:
            A message indicating that the workspace invitation has been rejected.
        """
        db_obj = await workspace_invitations_service.get(item_id=invitation_id)
        if db_obj.workspace_id != workspace_id:
            raise HTTPException(status_code=400, detail="Invitation does not belong to this workspace")
        if db_obj.email != current_user.email:
            raise HTTPException(status_code=400, detail="You are not authorized to reject this invitation")
        await workspace_invitations_service.delete(item_id=invitation_id)
        return Message(message="Workspace invitation rejected")
