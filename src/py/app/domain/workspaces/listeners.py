"""Workspace domain signals/events."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from litestar.events import listener

from app.domain.accounts.deps import provide_users_service
from app.domain.workspaces import deps
from app.lib.deps import provide_services

if TYPE_CHECKING:
    from uuid import UUID

    from app.lib.email import AppEmailService


logger = structlog.get_logger()


@listener("workspace_created")
async def workspace_created_event_handler(workspace_id: UUID) -> None:
    """Executes when a new workspace is created.

    Args:
        workspace_id: The primary key of the workspace that was created.
    """
    await logger.ainfo("Running post workspace creation flow.")
    async with provide_services(deps.provide_workspaces_service) as (service,):
        obj = await service.get_one_or_none(id=workspace_id)
        if obj is None:
            await logger.aerror("Could not locate the specified workspace", id=workspace_id)
        else:
            await logger.ainfo("Found workspace", **obj.to_dict())


@listener("workspace_invitation_created")
async def workspace_invitation_created_event_handler(invitation_id: UUID, mailer: AppEmailService) -> None:
    """Executes when a new workspace invitation is created.

    Args:
        invitation_id: The workspace invitation ID.
        mailer: The application email service.
    """
    await logger.ainfo("Running post workspace invitation creation flow.")
    async with provide_services(
        deps.provide_workspace_invitations_service, deps.provide_workspaces_service, provide_users_service
    ) as (
        workspace_invitations_service,
        workspaces_service,
        users_service,
    ):
        invitation = await workspace_invitations_service.get_one_or_none(id=invitation_id)
        if invitation is None:
            await logger.aerror("Could not locate the specified workspace invitation", id=invitation_id)
            return

        inviter = await users_service.get_one_or_none(id=invitation.invited_by_id)
        if inviter is None:
            await logger.aerror("Could not locate the inviter", id=invitation.invited_by_id)
            return

        workspace = await workspaces_service.get_one_or_none(id=invitation.workspace_id)
        if workspace is None:
            await logger.aerror("Could not locate the workspace", id=invitation.workspace_id)
            return

        await mailer.send_workspace_invitation_email(
            invitee_email=invitation.email,
            inviter_name=inviter.name or inviter.email,
            workspace_name=workspace.name,
            invitation_url=f"{mailer.base_url}/workspaces/{workspace.id}/invitations/{invitation.id}/accept",
        )

        await logger.ainfo("Sent workspace invitation email", invitation_id=invitation.id)


__all__ = (
    "workspace_created_event_handler",
    "workspace_invitation_created_event_handler",
)
