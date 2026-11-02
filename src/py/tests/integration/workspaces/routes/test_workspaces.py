"""Integration tests for workspace management endpoints.

This module combines tests from:
- test_workspace_endpoints.py (workspace CRUD and member operations)
- test_workspace_management.py (workspace lifecycle and permissions)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

import pytest
from litestar_email import InMemoryBackend
from sqlalchemy import select

from app.db import models as m
from app.lib.crypt import get_password_hash
from tests.factories import WorkspaceFactory, WorkspaceMemberFactory, UserFactory, create_workspace_with_members, create_user_with_workspace

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from httpx import AsyncClient
    from litestar.testing import AsyncTestClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.anyio, pytest.mark.integration, pytest.mark.workspaces, pytest.mark.endpoints]


@pytest.fixture(autouse=True)
def clear_email_outbox() -> None:
    """Clear email outbox before each test."""
    InMemoryBackend.clear()


async def _login_user(client: AsyncClient, user: m.User, password: str = "testPassword123!") -> str:
    """Helper to login user and return auth token."""
    response = await client.post(
        "/api/access/login",
        data={"username": user.email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 201
    return cast("str", response.json()["access_token"])


# =============================================================================
# Workspace CRUD Tests
# =============================================================================


async def test_create_workspace_success(authenticated_client: AsyncTestClient) -> None:
    """Test successful workspace creation."""
    workspace_data = {
        "name": "Test Workspace",
        "description": "A test workspace for integration testing",
    }

    response = await authenticated_client.post("/api/workspaces", json=workspace_data)

    assert response.status_code == 201
    workspace = response.json()
    assert workspace["name"] == "Test Workspace"
    assert workspace["description"] == "A test workspace for integration testing"
    assert workspace["slug"] is not None
    assert workspace["isActive"] is True


async def test_create_workspace_with_session(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successful workspace creation with database verification."""
    user = UserFactory.build(
        email="work_space_creator@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.commit()

    token = await _login_user(client, user)

    response = await client.post(
        "/api/workspaces",
        json={"name": "My New Test Workspace", "description": "A test workspace", "tags": ["development", "testing"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == "My New Test Workspace"
    assert response_data["description"] == "A test workspace"
    assert len(response_data["members"]) == 1
    assert response_data["members"][0]["email"] == user.email
    assert response_data["members"][0]["isOwner"] is True
    assert response_data["members"][0]["role"] == m.WorkspaceRoles.ADMIN.value

    result = await session.execute(select(m.Workspace).where(m.Workspace.name == "My New Test Workspace"))
    workspace = result.scalar_one_or_none()
    assert workspace is not None
    membership_result = await session.execute(
        select(m.WorkspaceMember).where(m.WorkspaceMember.workspace_id == workspace.id, m.WorkspaceMember.user_id == user.id)
    )
    membership = membership_result.scalar_one_or_none()
    assert membership is not None
    assert membership.is_owner is True
    assert membership.role == m.WorkspaceRoles.ADMIN


async def test_create_workspace_unauthenticated(client: AsyncTestClient) -> None:
    """Test workspace creation without authentication fails."""
    workspace_data = {
        "name": "Test Workspace",
        "description": "A test workspace",
    }

    response = await client.post("/api/workspaces", json=workspace_data)

    assert response.status_code == 401


async def test_create_workspace_invalid_data(authenticated_client: AsyncTestClient) -> None:
    """Test workspace creation with invalid data."""
    workspace_data = {
        "description": "A test workspace without name",
    }

    response = await authenticated_client.post("/api/workspaces", json=workspace_data)

    assert response.status_code == 400


async def test_get_user_workspaces(
    authenticated_client: AsyncTestClient,
    test_user: m.User,
    test_workspace: m.Workspace,
) -> None:
    """Test getting user's workspaces."""
    response = await authenticated_client.get("/api/workspaces")

    assert response.status_code == 200
    workspaces_response = response.json()
    workspaces = workspaces_response["items"]
    assert len(workspaces) >= 1
    workspace_ids = [workspace["id"] for workspace in workspaces]
    assert str(test_workspace.id) in workspace_ids


async def test_get_user_workspaces_unauthenticated(client: AsyncTestClient) -> None:
    """Test getting workspaces without authentication fails."""
    response = await client.get("/api/workspaces")

    assert response.status_code == 401


async def test_list_workspaces_as_member(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test listing workspaces where user is a member."""
    user, workspace1 = await create_user_with_workspace(session)

    other_user = UserFactory.build()
    other_workspace = WorkspaceFactory.build()
    session.add_all([other_user, other_workspace])
    await session.flush()

    other_membership = WorkspaceMemberFactory.build(
        workspace_id=other_workspace.id, user_id=other_user.id, role=m.WorkspaceRoles.ADMIN, is_owner=True
    )
    session.add(other_membership)

    user.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, user)

    response = await client.get("/api/workspaces", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    response_data = response.json()

    workspace_ids = [workspace["id"] for workspace in response_data["items"]]
    assert str(workspace1.id) in workspace_ids
    assert str(other_workspace.id) not in workspace_ids


async def test_get_workspace_details(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
) -> None:
    """Test getting workspace details."""
    response = await authenticated_client.get(f"/api/workspaces/{test_workspace.id}")

    assert response.status_code == 200
    workspace = response.json()
    assert workspace["id"] == str(test_workspace.id)
    assert workspace["name"] == test_workspace.name
    assert workspace["description"] == test_workspace.description


async def test_get_workspace_details_not_member(
    client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test getting workspace details when not a member."""
    other_user = m.User(
        id=uuid4(),
        email="other@example.com",
        name="Other User",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(other_user)
    await session.commit()

    login_response = await client.post(
        "/api/access/login", data={"username": other_user.email, "password": "TestPassword123!"}
    )

    if login_response.status_code == 201:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get(f"/api/workspaces/{test_workspace.id}", headers=headers)

        assert response.status_code in [403, 404]


async def test_get_workspace_details_nonexistent(authenticated_client: AsyncTestClient) -> None:
    """Test getting details for non-existent workspace."""
    response = await authenticated_client.get(f"/api/workspaces/{uuid4()}")

    assert response.status_code == 403


async def test_update_workspace(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
) -> None:
    """Test updating workspace information."""
    update_data = {
        "name": "Updated Workspace Name",
        "description": "Updated description",
    }

    response = await authenticated_client.patch(f"/api/workspaces/{test_workspace.id}", json=update_data)

    assert response.status_code == 200
    workspace = response.json()
    assert workspace["name"] == "Updated Workspace Name"
    assert workspace["description"] == "Updated description"


async def test_update_workspace_as_admin(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test updating workspace as admin with database verification."""
    user, workspace = await create_user_with_workspace(session)
    user.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, user)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}",
        json={"name": "Updated Workspace Name", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Workspace Name"
    assert response_data["description"] == "Updated description"

    await session.refresh(workspace)
    assert workspace.name == "Updated Workspace Name"
    assert workspace.description == "Updated description"


async def test_update_workspace_as_member(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test updating workspace as regular member (should fail)."""
    _owner, workspace = await create_user_with_workspace(session)

    member = UserFactory.build(
        hashed_password=await get_password_hash("testPassword123!"), is_active=True, is_verified=True
    )
    session.add(member)
    await session.flush()

    membership = WorkspaceMemberFactory.build(workspace_id=workspace.id, user_id=member.id, role=m.WorkspaceRoles.MEMBER, is_owner=False)
    session.add(membership)
    await session.commit()

    token = await _login_user(client, member)

    response = await client.patch(
        f"/api/workspaces/{workspace.id}",
        json={"name": "Should Not Update"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


async def test_update_workspace_not_authorized(
    client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test updating workspace when not authorized."""
    other_user = m.User(
        id=uuid4(),
        email="unauthorized@example.com",
        name="Unauthorized User",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(other_user)
    await session.commit()

    login_response = await client.post(
        "/api/access/login", data={"username": other_user.email, "password": "TestPassword123!"}
    )

    if login_response.status_code == 201:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Unauthorized Update"}

        response = await client.patch(f"/api/workspaces/{test_workspace.id}", json=update_data, headers=headers)

        assert response.status_code in [403, 404]


async def test_delete_workspace(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
) -> None:
    """Test deleting a workspace."""
    response = await authenticated_client.delete(f"/api/workspaces/{test_workspace.id}")

    assert response.status_code in [200, 204]


async def test_delete_workspace_as_admin(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test deleting workspace as admin with database verification."""
    user, workspace = await create_user_with_workspace(session)
    user.hashed_password = await get_password_hash("testPassword123!")
    workspace_id = workspace.id
    await session.commit()

    token = await _login_user(client, user)

    response = await client.delete(f"/api/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204

    result = await session.execute(select(m.Workspace).where(m.Workspace.id == workspace_id))
    deleted_workspace = result.scalar_one_or_none()
    assert deleted_workspace is None


async def test_delete_workspace_not_owner(
    client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test deleting workspace when not owner."""
    member_user = m.User(
        id=uuid4(),
        email="member@example.com",
        name="Member User",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(member_user)
    await session.commit()

    membership = m.WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=member_user.id,
        role=m.WorkspaceRoles.MEMBER,
        is_owner=False,
    )
    session.add(membership)
    await session.commit()

    login_response = await client.post(
        "/api/access/login", data={"username": member_user.email, "password": "TestPassword123!"}
    )

    if login_response.status_code == 201:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.delete(f"/api/workspaces/{test_workspace.id}", headers=headers)

        assert response.status_code == 403


# =============================================================================
# Workspace Member Tests
# =============================================================================


async def test_get_workspace_members(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
) -> None:
    """Test getting workspace members via workspace detail response."""
    response = await authenticated_client.get(f"/api/workspaces/{test_workspace.id}")

    assert response.status_code == 200
    workspace = response.json()
    members = workspace.get("members", [])
    assert len(members) >= 1


async def test_add_workspace_member(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test adding a workspace member."""
    new_member = m.User(
        id=uuid4(),
        email="newmember@example.com",
        name="New Member",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(new_member)
    await session.commit()

    member_data = {
        "userName": new_member.email,
    }

    response = await authenticated_client.post(f"/api/workspaces/{test_workspace.id}/members", json=member_data)

    assert response.status_code == 201
    workspace = response.json()
    assert "id" in workspace
    member_emails = [member.get("email") or member.get("user", {}).get("email") for member in workspace.get("members", [])]
    assert new_member.email in member_emails


async def test_add_member_to_workspace_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successfully adding a member to a workspace with database verification."""
    owner, workspace = await create_user_with_workspace(session)
    owner.hashed_password = await get_password_hash("testPassword123!")

    new_member = UserFactory.build(email="newmember@example.com", is_active=True, is_verified=True)
    session.add(new_member)
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/members",
        json={"userName": "newmember@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    response_data = response.json()

    member_emails = [
        member.get("user", {}).get("email") or member.get("email") for member in response_data.get("members", [])
    ]
    assert "newmember@example.com" in member_emails

    result = await session.execute(
        select(m.WorkspaceMember).where(m.WorkspaceMember.workspace_id == workspace.id, m.WorkspaceMember.user_id == new_member.id)
    )
    membership = result.scalar_one_or_none()
    assert membership is not None
    assert membership.role == m.WorkspaceRoles.MEMBER


async def test_add_member_already_exists(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test adding a member who is already in the workspace."""
    workspace, members = await create_workspace_with_members(session, member_count=2)
    owner = members[0]
    existing_member = members[1]

    owner.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/members",
        json={"userName": existing_member.email},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in {409, 500}


async def test_add_member_nonexistent_user(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test adding a non-existent user to a workspace."""
    owner, workspace = await create_user_with_workspace(session)
    owner.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.post(
        f"/api/workspaces/{workspace.id}/members",
        json={"userName": "nonexistent@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in {404, 500}


async def test_remove_workspace_member(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test removing a workspace member."""
    member_to_remove = m.User(
        id=uuid4(),
        email="removeme@example.com",
        name="Remove Me",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(member_to_remove)
    await session.commit()

    membership = m.WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=member_to_remove.id,
        role=m.WorkspaceRoles.MEMBER,
        is_owner=False,
    )
    session.add(membership)
    await session.commit()

    response = await authenticated_client.request(
        "DELETE",
        f"/api/workspaces/{test_workspace.id}/members",
        json={"userName": member_to_remove.email},
    )

    assert response.status_code == 202


async def test_remove_member_from_workspace_success(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test successfully removing a member from a workspace with database verification."""
    workspace, members = await create_workspace_with_members(session, member_count=3)
    owner = members[0]
    member_to_remove = members[1]

    owner.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.request(
        "DELETE",
        f"/api/workspaces/{workspace.id}/members",
        json={"userName": member_to_remove.email},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 202
    response_data = response.json()

    member_emails = [member["email"] for member in response_data["members"]]
    assert member_to_remove.email not in member_emails

    result = await session.execute(
        select(m.WorkspaceMember).where(m.WorkspaceMember.workspace_id == workspace.id, m.WorkspaceMember.user_id == member_to_remove.id)
    )
    membership = result.scalar_one_or_none()
    assert membership is None


async def test_update_member_role(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    session: AsyncSession,
) -> None:
    """Test updating a workspace member's role."""
    member_user = m.User(
        id=uuid4(),
        email="promoteme@example.com",
        name="Promote Me",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(member_user)
    await session.commit()

    membership = m.WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=member_user.id,
        role=m.WorkspaceRoles.MEMBER,
        is_owner=False,
    )
    session.add(membership)
    await session.commit()

    update_data = {"role": m.WorkspaceRoles.ADMIN.value}

    response = await authenticated_client.patch(f"/api/workspaces/{test_workspace.id}/members/{member_user.id}", json=update_data)

    assert response.status_code == 200
    membership = response.json()
    assert membership["role"] == m.WorkspaceRoles.ADMIN.value


# =============================================================================
# Workspace Invitation Tests
# =============================================================================


async def test_invite_workspace_member(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    await_events: Callable[[], Coroutine[Any, Any, None]],
) -> None:
    """Test inviting a workspace member."""
    invitation_data = {
        "email": "newmember@example.com",
        "role": m.WorkspaceRoles.MEMBER.value,
    }

    response = await authenticated_client.post(
        f"/api/workspaces/{test_workspace.id}/invitations",
        json=invitation_data,
    )

    assert response.status_code == 201
    invitation = response.json()
    assert invitation["email"] == "newmember@example.com"
    assert invitation["role"] == m.WorkspaceRoles.MEMBER.value
    assert invitation["isAccepted"] is False

    await await_events()
    assert len(InMemoryBackend.outbox) == 1
    assert "newmember@example.com" in InMemoryBackend.outbox[0].to


async def test_invite_existing_member(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    test_user: m.User,
) -> None:
    """Test inviting someone who is already a member."""
    invitation_data = {
        "email": test_user.email,
        "role": m.WorkspaceRoles.MEMBER.value,
    }

    response = await authenticated_client.post(f"/api/workspaces/{test_workspace.id}/invitations", json=invitation_data)

    assert response.status_code == 400


async def test_get_workspace_invitations(
    authenticated_client: AsyncTestClient,
    test_workspace: m.Workspace,
    test_workspace_invitation: m.WorkspaceInvitation,
) -> None:
    """Test getting workspace invitations."""
    response = await authenticated_client.get(f"/api/workspaces/{test_workspace.id}/invitations")

    assert response.status_code == 200
    response_data = response.json()
    invitations = response_data["items"]
    assert len(invitations) >= 1
    invitation_emails = [inv["email"] for inv in invitations]
    assert test_workspace_invitation.email in invitation_emails


async def test_accept_workspace_invitation(
    client: AsyncTestClient,
    test_workspace_invitation: m.WorkspaceInvitation,
    session: AsyncSession,
) -> None:
    """Test accepting a workspace invitation."""
    invited_user = m.User(
        id=uuid4(),
        email=test_workspace_invitation.email,
        name="Invited User",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invited_user)
    await session.commit()

    login_response = await client.post(
        "/api/access/login", data={"username": invited_user.email, "password": "TestPassword123!"}
    )
    assert login_response.status_code == 201
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/workspaces/{test_workspace_invitation.workspace_id}/invitations/{test_workspace_invitation.id}/accept",
        headers=headers,
    )

    assert response.status_code == 201
    result = response.json()
    assert "accepted" in result["message"].lower() or "joined" in result["message"].lower()


async def test_reject_workspace_invitation(
    client: AsyncTestClient,
    test_workspace_invitation: m.WorkspaceInvitation,
    session: AsyncSession,
) -> None:
    """Test rejecting a workspace invitation."""
    invited_user = m.User(
        id=uuid4(),
        email=test_workspace_invitation.email,
        name="Invited User",
        hashed_password=await get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    session.add(invited_user)
    await session.commit()

    login_response = await client.post(
        "/api/access/login",
        data={"username": invited_user.email, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 201
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/workspaces/{test_workspace_invitation.workspace_id}/invitations/{test_workspace_invitation.id}/reject",
        headers=headers,
    )

    assert response.status_code == 201
    result = response.json()
    assert "rejected" in result["message"].lower() or "declined" in result["message"].lower()


async def test_cancel_workspace_invitation(
    authenticated_client: AsyncTestClient,
    test_workspace_invitation: m.WorkspaceInvitation,
) -> None:
    """Test canceling a workspace invitation."""
    response = await authenticated_client.delete(
        f"/api/workspaces/{test_workspace_invitation.workspace_id}/invitations/{test_workspace_invitation.id}"
    )

    assert response.status_code in [200, 204]


# =============================================================================
# Permission Tests
# =============================================================================


async def test_workspace_owner_permissions(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test that workspace owners have all permissions."""
    owner, workspace = await create_user_with_workspace(session)
    owner.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.get(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.patch(
        f"/api/workspaces/{workspace.id}", json={"name": "Updated by Owner"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


async def test_workspace_admin_permissions(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test that workspace admins have appropriate permissions."""
    _owner, workspace = await create_user_with_workspace(session)

    admin = UserFactory.build(
        hashed_password=await get_password_hash("testPassword123!"), is_active=True, is_verified=True
    )
    session.add(admin)
    await session.flush()

    admin_membership = WorkspaceMemberFactory.build(
        workspace_id=workspace.id, user_id=admin.id, role=m.WorkspaceRoles.ADMIN, is_owner=False
    )
    session.add(admin_membership)
    await session.commit()

    token = await _login_user(client, admin)

    response = await client.get(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.patch(
        f"/api/workspaces/{workspace.id}", json={"name": "Updated by Admin"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


async def test_workspace_member_permissions(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test that workspace members have limited permissions."""
    _owner, workspace = await create_user_with_workspace(session)

    member = UserFactory.build(
        hashed_password=await get_password_hash("testPassword123!"), is_active=True, is_verified=True
    )
    session.add(member)
    await session.flush()

    member_membership = WorkspaceMemberFactory.build(
        workspace_id=workspace.id, user_id=member.id, role=m.WorkspaceRoles.MEMBER, is_owner=False
    )
    session.add(member_membership)
    await session.commit()

    token = await _login_user(client, member)

    response = await client.get(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.patch(
        f"/api/workspaces/{workspace.id}",
        json={"name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

    response = await client.delete(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


async def test_non_member_permissions(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test that non-members have no access to workspace."""
    _owner, workspace = await create_user_with_workspace(session)

    non_member = UserFactory.build(
        hashed_password=await get_password_hash("testPassword123!"), is_active=True, is_verified=True
    )
    session.add(non_member)
    await session.commit()

    token = await _login_user(client, non_member)

    response = await client.get(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    response = await client.patch(
        f"/api/workspaces/{workspace.id}",
        json={"name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

    response = await client.delete(f"/api/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# =============================================================================
# Seeded Data Tests
# =============================================================================


async def test_workspaces_with_no_auth(client: AsyncTestClient) -> None:
    response = await client.patch("/api/workspaces/97108ac1-ffcb-411d-8b1e-d9183399f63b", json={"name": "TEST UPDATE"})
    assert response.status_code == 401
    response = await client.post(
        "/api/workspaces/",
        json={"name": "A User", "email": "new-user@example.com", "password": "S3cret!"},
    )
    assert response.status_code == 401
    response = await client.get("/api/workspaces/97108ac1-ffcb-411d-8b1e-d9183399f63b")
    assert response.status_code == 401
    response = await client.get("/api/workspaces")
    assert response.status_code == 401
    response = await client.delete("/api/workspaces/97108ac1-ffcb-411d-8b1e-d9183399f63b")
    assert response.status_code == 401


async def test_workspaces_with_incorrect_role(
    client: AsyncTestClient,
    user_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.patch(
        "/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999",
        json={"name": "TEST UPDATE"},
        headers=user_token_headers,
    )
    assert response.status_code == 403
    response = await client.post(
        "/api/workspaces/",
        json={"name": "A new workspace."},
        headers=user_token_headers,
    )
    assert response.status_code == 201
    response = await client.get("/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999", headers=user_token_headers)
    assert response.status_code == 403
    response = await client.get("/api/workspaces", headers=user_token_headers)
    assert response.status_code == 200
    response = await client.delete("/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999", headers=user_token_headers)
    assert response.status_code == 403


async def test_workspaces_list(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.get("/api/workspaces", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_workspaces_get(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.get("/api/workspaces/97108ac1-ffcb-411d-8b1e-d9183399f63b", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Workspace"


async def test_workspaces_create(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.post(
        "/api/workspaces/",
        json={"name": "My First Workspace", "tags": ["cool tag"]},
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_workspaces_update(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.patch(
        "/api/workspaces/97108ac1-ffcb-411d-8b1e-d9183399f63b",
        json={"name": "Name Changed"},
        headers=superuser_token_headers,
    )
    assert response.status_code == 200


async def test_workspaces_delete(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.delete(
        "/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204
    response = await client.get(
        "/api/users/5ef29f3c-3560-4d15-ba6b-a2e5c721e999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200


async def test_workspaces_add_remove_member(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.post(
        "/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999/members",
        headers=superuser_token_headers,
        json={"userName": "user@example.com"},
    )
    assert response.status_code == 201
    assert "user@example.com" in [e["email"] for e in response.json()["members"]]

    response = await client.request(
        "DELETE",
        "/api/workspaces/81108ac1-ffcb-411d-8b1e-d91833999999/members",
        headers=superuser_token_headers,
        json={"userName": "user@example.com"},
    )
    assert response.status_code == 202
    assert "user@example.com" not in [e["email"] for e in response.json()["members"]]


async def test_tags_list(
    client: AsyncTestClient,
    superuser_token_headers: dict[str, str],
    seeded_db: None,
) -> None:
    response = await client.get("/api/tags", headers=superuser_token_headers)
    resj = response.json()
    assert response.status_code == 200
    assert int(resj["total"]) >= 3


# =============================================================================
# Lifecycle Tests
# =============================================================================


async def test_complete_workspace_lifecycle(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test complete workspace creation, management, and deletion workflow."""
    owner = UserFactory.build(
        email="owner@example.com",
        hashed_password=await get_password_hash("testPassword123!"),
        is_active=True,
        is_verified=True,
    )
    member1 = UserFactory.build(email="member1@example.com", is_active=True, is_verified=True)
    member2 = UserFactory.build(email="member2@example.com", is_active=True, is_verified=True)
    session.add_all([owner, member1, member2])
    await session.commit()

    token = await _login_user(client, owner)

    response = await client.post(
        "/api/workspaces",
        json={"name": "Full Lifecycle Workspace", "description": "Test workspace for complete workflow"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    workspace_data = response.json()
    workspace_id = workspace_data["id"]

    response = await client.post(
        f"/api/workspaces/{workspace_id}/members",
        json={"userName": "member1@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/workspaces/{workspace_id}/members",
        json={"userName": "member2@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    response = await client.get(f"/api/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    workspace_data = response.json()
    assert len(workspace_data["members"]) == 3

    response = await client.patch(
        f"/api/workspaces/{workspace_id}",
        json={"name": "Updated Lifecycle Workspace", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = await client.request(
        "DELETE",
        f"/api/workspaces/{workspace_id}/members",
        json={"userName": "member2@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202

    response = await client.get(f"/api/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    workspace_data = response.json()
    assert len(workspace_data["members"]) == 2
    member_emails = [member.get("user", {}).get("email") or member.get("email") for member in workspace_data["members"]]
    assert "member2@example.com" not in member_emails

    response = await client.delete(f"/api/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    response = await client.get(f"/api/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in {403, 404}


async def test_workspace_security_isolation(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Test that workspace data is properly isolated between workspaces."""
    owner1, workspace1 = await create_user_with_workspace(session)
    owner2, workspace2 = await create_user_with_workspace(session)

    owner1.hashed_password = await get_password_hash("testPassword123!")
    owner2.hashed_password = await get_password_hash("testPassword123!")
    await session.commit()

    token1 = await _login_user(client, owner1)
    token2 = await _login_user(client, owner2)

    response = await client.get("/api/workspaces", headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 200
    workspaces_data = response.json()
    workspace_ids = [workspace["id"] for workspace in workspaces_data["items"]]
    assert str(workspace1.id) in workspace_ids
    assert str(workspace2.id) not in workspace_ids

    response = await client.get("/api/workspaces", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200
    workspaces_data = response.json()
    workspace_ids = [workspace["id"] for workspace in workspaces_data["items"]]
    assert str(workspace2.id) in workspace_ids
    assert str(workspace1.id) not in workspace_ids

    response = await client.get(f"/api/workspaces/{workspace2.id}", headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 403

    response = await client.get(f"/api/workspaces/{workspace1.id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 403
