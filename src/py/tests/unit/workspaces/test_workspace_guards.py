"""Comprehensive tests for workspace domain guards."""

from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

import pytest
from litestar.exceptions import PermissionDeniedException

from app.db import models as m
from app.domain.workspaces.guards import (
    requires_workspace_admin,
    requires_workspace_membership,
    requires_workspace_ownership,
)
from app.lib import constants

pytestmark = [pytest.mark.anyio, pytest.mark.unit, pytest.mark.auth, pytest.mark.security, pytest.mark.workspaces]


def test_membership_superuser_flag_passes() -> None:
    """Test that is_superuser=True passes the guard."""
    workspace_id = uuid4()

    mock_user = Mock()
    mock_user.is_superuser = True
    mock_user.roles = []
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_membership(mock_connection, mock_handler)


def test_membership_superuser_role_passes() -> None:
    """Test that user with SUPERUSER_ACCESS_ROLE passes."""
    workspace_id = uuid4()

    mock_role = Mock()
    mock_role.role_name = constants.SUPERUSER_ACCESS_ROLE

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = [mock_role]
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_membership(mock_connection, mock_handler)


def test_workspace_member_passes() -> None:
    """Test that workspace member passes the guard."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_membership(mock_connection, mock_handler)


def test_non_member_raises_permission_denied() -> None:
    """Test that non-member raises PermissionDeniedException."""
    workspace_id = uuid4()
    other_workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = other_workspace_id  # Different workspace

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException) as exc_info:
        requires_workspace_membership(mock_connection, mock_handler)

    assert "Insufficient permissions" in str(exc_info.value.detail)


def test_no_workspaces_raises_permission_denied() -> None:
    """Test that user with no workspaces raises PermissionDeniedException."""
    workspace_id = uuid4()

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException) as exc_info:
        requires_workspace_membership(mock_connection, mock_handler)

    assert "Insufficient permissions" in str(exc_info.value.detail)


def test_non_superuser_role_fails() -> None:
    """Test that user with non-superuser role fails."""
    workspace_id = uuid4()

    mock_role = Mock()
    mock_role.role_name = "regular_user"

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = [mock_role]
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException):
        requires_workspace_membership(mock_connection, mock_handler)


def test_admin_superuser_flag_passes() -> None:
    """Test that is_superuser=True passes the guard."""
    workspace_id = uuid4()

    mock_user = Mock()
    mock_user.is_superuser = True
    mock_user.roles = []
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_admin(mock_connection, mock_handler)


def test_admin_superuser_role_passes() -> None:
    """Test that user with SUPERUSER_ACCESS_ROLE passes."""
    workspace_id = uuid4()

    mock_role = Mock()
    mock_role.role_name = constants.SUPERUSER_ACCESS_ROLE

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = [mock_role]
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_admin(mock_connection, mock_handler)


def test_workspace_admin_passes() -> None:
    """Test that workspace admin passes the guard."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.ADMIN

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_admin(mock_connection, mock_handler)


def test_workspace_member_fails() -> None:
    """Test that regular workspace member fails admin guard."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.MEMBER  # Not admin

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException) as exc_info:
        requires_workspace_admin(mock_connection, mock_handler)

    assert "Insufficient permissions" in str(exc_info.value.detail)


def test_admin_of_different_workspace_fails() -> None:
    """Test that admin of different workspace fails."""
    workspace_id = uuid4()
    other_workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = other_workspace_id  # Different workspace

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.ADMIN

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException):
        requires_workspace_admin(mock_connection, mock_handler)


def test_ownership_superuser_flag_passes() -> None:
    """Test that is_superuser=True passes the guard."""
    workspace_id = uuid4()

    mock_user = Mock()
    mock_user.is_superuser = True
    mock_user.roles = []
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_ownership(mock_connection, mock_handler)


def test_ownership_superuser_role_passes() -> None:
    """Test that user with SUPERUSER_ACCESS_ROLE passes."""
    workspace_id = uuid4()

    mock_role = Mock()
    mock_role.role_name = constants.SUPERUSER_ACCESS_ROLE

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = [mock_role]
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_ownership(mock_connection, mock_handler)


def test_workspace_owner_passes() -> None:
    """Test that workspace owner passes the guard."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.is_owner = True

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should not raise
    requires_workspace_ownership(mock_connection, mock_handler)


def test_workspace_admin_non_owner_fails() -> None:
    """Test that workspace admin who is not owner fails."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.is_owner = False  # Not owner

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException) as exc_info:
        requires_workspace_ownership(mock_connection, mock_handler)

    assert "Insufficient permissions" in str(exc_info.value.detail)


def test_owner_of_different_workspace_fails() -> None:
    """Test that owner of different workspace fails."""
    workspace_id = uuid4()
    other_workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = other_workspace_id  # Different workspace

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.is_owner = True

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException):
        requires_workspace_ownership(mock_connection, mock_handler)


def test_no_memberships_fails() -> None:
    """Test that user with no memberships fails."""
    workspace_id = uuid4()

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = []

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    with pytest.raises(PermissionDeniedException):
        requires_workspace_ownership(mock_connection, mock_handler)


def test_owner_passes_all_guards() -> None:
    """Test that workspace owner passes all guards."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.ADMIN
    mock_membership.is_owner = True

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # All guards should pass
    requires_workspace_membership(mock_connection, mock_handler)
    requires_workspace_admin(mock_connection, mock_handler)
    requires_workspace_ownership(mock_connection, mock_handler)


def test_admin_passes_membership_and_admin() -> None:
    """Test that admin passes membership and admin guards but not ownership."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.ADMIN
    mock_membership.is_owner = False

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should pass membership and admin
    requires_workspace_membership(mock_connection, mock_handler)
    requires_workspace_admin(mock_connection, mock_handler)

    # Should fail ownership
    with pytest.raises(PermissionDeniedException):
        requires_workspace_ownership(mock_connection, mock_handler)


def test_member_passes_only_membership() -> None:
    """Test that regular member only passes membership guard."""
    workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership = Mock()
    mock_membership.workspace = mock_workspace
    mock_membership.role = m.WorkspaceRoles.MEMBER
    mock_membership.is_owner = False

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should pass membership
    requires_workspace_membership(mock_connection, mock_handler)

    # Should fail admin and ownership
    with pytest.raises(PermissionDeniedException):
        requires_workspace_admin(mock_connection, mock_handler)

    with pytest.raises(PermissionDeniedException):
        requires_workspace_ownership(mock_connection, mock_handler)


def test_member_of_requested_workspace_among_many() -> None:
    """Test user who is member of requested workspace among multiple workspaces."""
    workspace_id = uuid4()
    other_workspace_id = uuid4()

    mock_workspace = Mock()
    mock_workspace.id = other_workspace_id

    mock_workspace = Mock()
    mock_workspace.id = workspace_id

    mock_membership1 = Mock()
    mock_membership1.workspace = mock_workspace

    mock_membership2 = Mock()
    mock_membership2.workspace = mock_workspace

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_membership1, mock_membership2]

    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": workspace_id}
    mock_handler = Mock()

    # Should pass
    requires_workspace_membership(mock_connection, mock_handler)


def test_admin_in_one_member_in_another() -> None:
    """Test user who is admin in one workspace but member in another."""
    admin_workspace_id = uuid4()
    member_workspace_id = uuid4()

    mock_admin_workspace = Mock()
    mock_admin_workspace.id = admin_workspace_id

    mock_member_workspace = Mock()
    mock_member_workspace.id = member_workspace_id

    mock_admin_membership = Mock()
    mock_admin_membership.workspace = mock_admin_workspace
    mock_admin_membership.role = m.WorkspaceRoles.ADMIN
    mock_admin_membership.is_owner = False

    mock_member_membership = Mock()
    mock_member_membership.workspace = mock_member_workspace
    mock_member_membership.role = m.WorkspaceRoles.MEMBER
    mock_member_membership.is_owner = False

    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.roles = []
    mock_user.workspaces = [mock_admin_membership, mock_member_membership]

    mock_handler = Mock()

    # Should pass admin for admin_workspace
    mock_connection = Mock()
    mock_connection.user = mock_user
    mock_connection.path_params = {"workspace_id": admin_workspace_id}
    requires_workspace_admin(mock_connection, mock_handler)

    # Should fail admin for member_workspace
    mock_connection2 = Mock()
    mock_connection2.user = mock_user
    mock_connection2.path_params = {"workspace_id": member_workspace_id}
    with pytest.raises(PermissionDeniedException):
        requires_workspace_admin(mock_connection2, mock_handler)
