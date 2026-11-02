"""Integration tests for workspace invitation endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import uuid4

import pytest

from app.db import models as m
from app.lib.crypt import get_password_hash
from tests.factories import WorkspaceFactory, WorkspaceMemberFactory, UserFactory

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.anyio, pytest.mark.integration, pytest.mark.endpoints, pytest.mark.auth]


async def _login_user(client: AsyncClient, user: m.User) -> str:
    """Helper to login user and return auth token."""
    response = await client.post(
        "/api/access/login",
        data={"username": user.email, "password": "testPassword123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 201
    return cast("str", response.json()["access_token"])


async def _create_workspace_with_owner(session: AsyncSession, email_prefix: str = "owner") -> tuple[m.User, m.Workspace]:
    """Create a workspace with an owner user."""
    user = UserFactory.build(
        email=f"{email_prefix}-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    workspace = WorkspaceFactory.build(
        name=f"Test Workspace {uuid4().hex[:8]}",
        slug=f"test-workspace-{uuid4().hex[:8]}",
    )
    session.add_all([user, workspace])
    await session.flush()

    membership = WorkspaceMemberFactory.build(
        workspace_id=workspace.id,
        user_id=user.id,
        role=m.WorkspaceRoles.ADMIN,
        is_owner=True,
    )
    session.add(membership)
    await session.commit()
    await session.refresh(workspace, ["members"])
    return user, workspace


# --- Create Invitation Tests ---


async def test_create_invitation_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successful workspace invitation creation."""
    owner, workspace = await _create_workspace_with_owner(session, "inviteowner")
    token = await _login_user(client, owner)

    invitee_email = f"invitee-{uuid4().hex[:8]}@example.com"
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee_email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == invitee_email
    assert data["role"] == "MEMBER"
    assert data["isAccepted"] is False


async def test_create_invitation_already_member(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test invitation creation for already existing member."""
    owner, workspace = await _create_workspace_with_owner(session, "dupowner")
    token = await _login_user(client, owner)

    # Try to invite the owner (who is already a member)
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": owner.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "already a member" in response.text.lower()


async def test_create_invitation_unauthenticated(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test invitation creation without authentication."""
    _, workspace = await _create_workspace_with_owner(session, "unauthowner")

    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": "someone@example.com", "role": "MEMBER"},
    )

    assert response.status_code == 401


# --- List Invitations Tests ---


async def test_list_invitations_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test listing workspace invitations."""
    owner, workspace = await _create_workspace_with_owner(session, "listowner")
    token = await _login_user(client, owner)

    # Create an invitation
    invitee_email = f"listinvitee-{uuid4().hex[:8]}@example.com"
    await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee_email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List invitations
    response = await client.get(
        f"/api/workspaces/{workspace.id}/invitations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    emails = [item["email"] for item in data["items"]]
    assert invitee_email in emails


async def test_list_invitations_empty(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test listing invitations when none exist."""
    owner, workspace = await _create_workspace_with_owner(session, "emptyowner")
    token = await _login_user(client, owner)

    response = await client.get(
        f"/api/workspaces/{workspace.id}/invitations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 0


# --- Delete Invitation Tests ---


async def test_delete_invitation_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successful invitation deletion."""
    owner, workspace = await _create_workspace_with_owner(session, "delowner")
    token = await _login_user(client, owner)

    # Create an invitation
    invitee_email = f"delinvitee-{uuid4().hex[:8]}@example.com"
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee_email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )
    invitation_id = create_response.json()["id"]

    # Delete the invitation
    response = await client.delete(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    # Verify invitation is deleted
    list_response = await client.get(
        f"/api/workspaces/{workspace.id}/invitations",
        headers={"Authorization": f"Bearer {token}"},
    )
    emails = [item["email"] for item in list_response.json()["items"]]
    assert invitee_email not in emails


async def test_delete_invitation_wrong_workspace(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test deleting invitation from wrong workspace."""
    owner1, workspace1 = await _create_workspace_with_owner(session, "wrongworkspace1")
    _owner2, workspace2 = await _create_workspace_with_owner(session, "wrongworkspace2")
    token1 = await _login_user(client, owner1)

    # Create invitation on workspace1
    invitee_email = f"wronginvitee-{uuid4().hex[:8]}@example.com"
    create_response = await client.post(
        f"/api/workspaces/{workspace1.id}/invitations",
        json={"email": invitee_email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    invitation_id = create_response.json()["id"]

    # Try to delete from workspace2
    response = await client.delete(
        f"/api/workspaces/{workspace2.id}/invitations/{invitation_id}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    assert response.status_code == 400
    assert "does not belong" in response.text.lower()


# --- Accept Invitation Tests ---


async def test_accept_invitation_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successful invitation acceptance."""
    owner, workspace = await _create_workspace_with_owner(session, "acceptowner")
    owner_token = await _login_user(client, owner)

    # Create invitee user
    invitee = UserFactory.build(
        email=f"acceptinvitee-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invitee)
    await session.commit()

    # Create invitation
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Login as invitee and accept
    invitee_token = await _login_user(client, invitee)
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/accept",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "accepted" in data["message"].lower()


async def test_accept_invitation_already_accepted(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test accepting already accepted invitation."""
    owner, workspace = await _create_workspace_with_owner(session, "alreadyowner")
    owner_token = await _login_user(client, owner)

    # Create invitee user
    invitee = UserFactory.build(
        email=f"alreadyinvitee-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invitee)
    await session.commit()

    # Create and accept invitation
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    invitee_token = await _login_user(client, invitee)
    await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/accept",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    # Try to accept again
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/accept",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    assert response.status_code == 400
    assert "already" in response.text.lower()


async def test_accept_invitation_not_authorized(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test accepting invitation meant for different user."""
    owner, workspace = await _create_workspace_with_owner(session, "notauthowner")
    owner_token = await _login_user(client, owner)

    # Create invitation for someone else
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": "someoneelse@example.com", "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Create different user who tries to accept
    wrong_user = UserFactory.build(
        email=f"wronguser-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(wrong_user)
    await session.commit()

    wrong_user_token = await _login_user(client, wrong_user)
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/accept",
        headers={"Authorization": f"Bearer {wrong_user_token}"},
    )

    assert response.status_code == 400
    assert "not authorized" in response.text.lower()


async def test_accept_invitation_wrong_workspace(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test accepting invitation from wrong workspace."""
    owner, workspace1 = await _create_workspace_with_owner(session, "wrongw1")
    _, workspace2 = await _create_workspace_with_owner(session, "wrongw2")
    owner_token = await _login_user(client, owner)

    # Create invitee user
    invitee = UserFactory.build(
        email=f"wrongtinvitee-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invitee)
    await session.commit()

    # Create invitation on workspace1
    create_response = await client.post(
        f"/api/workspaces/{workspace1.id}/invitations",
        json={"email": invitee.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Try to accept from workspace2
    invitee_token = await _login_user(client, invitee)
    response = await client.post(
        f"/api/workspaces/{workspace2.id}/invitations/{invitation_id}/accept",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    assert response.status_code == 400
    assert "does not belong" in response.text.lower()


# --- Reject Invitation Tests ---


async def test_reject_invitation_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successful invitation rejection."""
    owner, workspace = await _create_workspace_with_owner(session, "rejectowner")
    owner_token = await _login_user(client, owner)

    # Create invitee user
    invitee = UserFactory.build(
        email=f"rejectinvitee-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invitee)
    await session.commit()

    # Create invitation
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": invitee.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Login as invitee and reject
    invitee_token = await _login_user(client, invitee)
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/reject",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "rejected" in data["message"].lower()


async def test_reject_invitation_not_authorized(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test rejecting invitation meant for different user."""
    owner, workspace = await _create_workspace_with_owner(session, "rejectnotauth")
    owner_token = await _login_user(client, owner)

    # Create invitation for someone else
    create_response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations",
        json={"email": "rejectsomeone@example.com", "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Create different user who tries to reject
    wrong_user = UserFactory.build(
        email=f"rejectwrong-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(wrong_user)
    await session.commit()

    wrong_user_token = await _login_user(client, wrong_user)
    response = await client.post(
        f"/api/workspaces/{workspace.id}/invitations/{invitation_id}/reject",
        headers={"Authorization": f"Bearer {wrong_user_token}"},
    )

    assert response.status_code == 400
    assert "not authorized" in response.text.lower()


async def test_reject_invitation_wrong_workspace(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test rejecting invitation from wrong workspace."""
    owner, workspace1 = await _create_workspace_with_owner(session, "rejwrong1")
    _, workspace2 = await _create_workspace_with_owner(session, "rejwrong2")
    owner_token = await _login_user(client, owner)

    # Create invitee user
    invitee = UserFactory.build(
        email=f"rejwronginvitee-{uuid4().hex[:8]}@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invitee)
    await session.commit()

    # Create invitation on workspace1
    create_response = await client.post(
        f"/api/workspaces/{workspace1.id}/invitations",
        json={"email": invitee.email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    invitation_id = create_response.json()["id"]

    # Try to reject from workspace2
    invitee_token = await _login_user(client, invitee)
    response = await client.post(
        f"/api/workspaces/{workspace2.id}/invitations/{invitation_id}/reject",
        headers={"Authorization": f"Bearer {invitee_token}"},
    )

    assert response.status_code == 400
    assert "does not belong" in response.text.lower()
