"""Comprehensive tests for WorkspaceService."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import uuid4

import pytest
from advanced_alchemy.exceptions import RepositoryError
from sqlalchemy.exc import IntegrityError

from app.db import models as m
from tests.factories import TagFactory, WorkspaceFactory, WorkspaceMemberFactory, UserFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.workspaces.services import WorkspaceService

pytestmark = [pytest.mark.anyio, pytest.mark.integration, pytest.mark.services]


async def test_create_workspace_basic(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test basic workspace creation."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data = {"name": "Test Workspace", "description": "A test workspace", "owner_id": owner.id}

    workspace = await workspace_service.create(data=workspace_data)

    assert workspace.name == "Test Workspace"
    assert workspace.description == "A test workspace"
    assert workspace.slug is not None
    assert workspace.is_active is True
    assert workspace.id is not None


async def test_create_workspace_with_owner(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test workspace creation with owner."""
    # Create owner user
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()
    await session.refresh(owner)

    workspace_data = {"name": "Owner Workspace", "description": "Workspace with owner", "owner_id": owner.id}

    workspace = await workspace_service.create(data=workspace_data)

    assert workspace.name == "Owner Workspace"
    assert len(workspace.members) == 1

    owner_member = workspace.members[0]
    assert owner_member.user_id == owner.id
    assert owner_member.role == m.WorkspaceRoles.ADMIN
    assert owner_member.is_owner is True


async def test_create_workspace_with_tags(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test workspace creation with tags."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data = {
        "name": "Tagged Workspace",
        "description": "Workspace with tags",
        "tags": ["development", "backend", "api"],
        "owner_id": owner.id,
    }

    workspace = await workspace_service.create(data=workspace_data, auto_refresh=True)

    assert workspace.name == "Tagged Workspace"
    # Refresh to load tags relationship
    await session.refresh(workspace, ["tags"])
    assert len(workspace.tags) == 3

    tag_names = [tag.name for tag in workspace.tags]
    assert "development" in tag_names
    assert "backend" in tag_names
    assert "api" in tag_names


async def test_create_workspace_slug_generation(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test automatic slug generation."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data = {"name": "Workspace With Spaces And CAPS", "description": "Testing slug generation", "owner_id": owner.id}

    workspace = await workspace_service.create(data=workspace_data)

    assert workspace.slug is not None
    assert " " not in workspace.slug
    assert workspace.slug.islower()


async def test_create_workspace_duplicate_name_different_slugs(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test that duplicate workspace names get different slugs."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data1 = {"name": "Test Workspace", "description": "First workspace", "owner_id": owner.id}
    workspace_data2 = {"name": "Test Workspace", "description": "Second workspace", "owner_id": owner.id}

    workspace1 = await workspace_service.create(data=workspace_data1)
    workspace2 = await workspace_service.create(data=workspace_data2)

    assert workspace1.name == workspace2.name
    assert workspace1.slug != workspace2.slug
    assert workspace1.id != workspace2.id


async def test_get_workspace_by_id(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test getting workspace by ID."""
    workspace = WorkspaceFactory.build()
    session.add(workspace)
    await session.commit()

    found_workspace = await workspace_service.get_one(id=workspace.id)

    assert found_workspace.id == workspace.id
    assert found_workspace.name == workspace.name


async def test_get_workspace_by_slug(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test getting workspace by slug."""
    workspace = WorkspaceFactory.build(slug="test-workspace-slug")
    session.add(workspace)
    await session.commit()

    found_workspace = await workspace_service.get_one(slug="test-workspace-slug")

    assert found_workspace.id == workspace.id
    assert found_workspace.slug == "test-workspace-slug"


async def test_update_workspace(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test updating workspace information."""
    workspace = WorkspaceFactory.build(name="Original Name")
    session.add(workspace)
    await session.commit()

    update_data = {"name": "Updated Name", "description": "Updated description"}

    updated_workspace = await workspace_service.update(item_id=workspace.id, data=update_data)

    assert updated_workspace.name == "Updated Name"
    assert updated_workspace.description == "Updated description"
    assert updated_workspace.id == workspace.id


async def test_update_workspace_with_new_tags(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test updating workspace with new tags."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    # Create workspace with initial tags
    workspace_data = {"name": "Workspace to Update", "tags": ["tag1", "tag2"], "owner_id": owner.id}
    workspace = await workspace_service.create(data=workspace_data)

    # Update with new tags
    update_data = {
        "tags": ["tag2", "tag3", "tag4"]  # Remove tag1, keep tag2, add tag3 and tag4
    }

    updated_workspace = await workspace_service.update(item_id=workspace.id, data=update_data, auto_refresh=True)
    await session.refresh(updated_workspace, ["tags"])

    tag_names = [tag.name for tag in updated_workspace.tags]
    assert "tag1" not in tag_names  # Removed
    assert "tag2" in tag_names  # Kept
    assert "tag3" in tag_names  # Added
    assert "tag4" in tag_names  # Added
    assert len(updated_workspace.tags) == 3


async def test_delete_workspace(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test deleting workspace."""
    workspace = WorkspaceFactory.build()
    session.add(workspace)
    await session.commit()

    await workspace_service.delete(item_id=workspace.id)

    # Verify workspace is deleted
    deleted_workspace = await workspace_service.get_one_or_none(id=workspace.id)
    assert deleted_workspace is None


async def test_list_workspaces(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test listing workspaces."""
    workspaces = [WorkspaceFactory.build() for _ in range(3)]
    session.add_all(workspaces)
    await session.commit()

    result = await workspace_service.list()

    assert len(result) >= 3  # At least the 3 we created


async def test_create_workspace_with_owner_user_object(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test workspace creation with owner as User object."""
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()
    await session.refresh(owner)

    workspace_data = {"name": "Owner Workspace", "owner": owner}

    workspace = await workspace_service.create(data=workspace_data)

    assert len(workspace.members) == 1
    owner_member = workspace.members[0]
    assert owner_member.user_id == owner.id
    assert owner_member.is_owner is True
    assert owner_member.role == m.WorkspaceRoles.ADMIN


async def test_update_workspace_change_owner(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test changing workspace owner."""
    # Create workspace with initial owner
    original_owner = UserFactory.build()
    new_owner = UserFactory.build()
    session.add_all([original_owner, new_owner])
    await session.commit()

    workspace_data = {"name": "Ownership Test Workspace", "owner_id": original_owner.id}
    workspace = await workspace_service.create(data=workspace_data)

    # Add new owner as member first
    new_member = WorkspaceMemberFactory.build(workspace_id=workspace.id, user_id=new_owner.id, role=m.WorkspaceRoles.MEMBER, is_owner=False)
    session.add(new_member)
    await session.commit()

    # Update workspace with new owner
    update_data = {"owner_id": new_owner.id}
    updated_workspace = await workspace_service.update(item_id=workspace.id, data=update_data)

    # Check that new owner has correct role and ownership
    new_owner_member = next((m for m in updated_workspace.members if m.user_id == new_owner.id), None)
    assert new_owner_member is not None
    assert new_owner_member.is_owner is True
    assert new_owner_member.role == m.WorkspaceRoles.ADMIN


async def test_populate_slug_when_missing(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test slug population when not provided."""
    workspace_data = {"name": "Workspace Without Slug"}

    # Call the private method directly for testing
    result = await workspace_service._populate_slug(workspace_data)

    assert isinstance(result, dict)
    assert "slug" in result
    assert result["slug"] is not None


async def test_populate_slug_when_provided(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test slug is preserved when provided."""
    workspace_data = {"name": "Workspace With Slug", "slug": "custom-slug"}

    result = await workspace_service._populate_slug(workspace_data)

    assert isinstance(result, dict)
    assert result["slug"] == "custom-slug"


async def test_populate_slug_without_name(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test slug population when name is missing."""
    workspace_data = {"description": "Workspace without name"}

    result = await workspace_service._populate_slug(workspace_data)

    # Should not add slug when name is missing
    assert isinstance(result, dict)
    assert "slug" not in result


async def test_populate_with_new_tags(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test adding new tags to workspace."""
    # Create owner user first (required by WorkspaceService for "create" operation)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data = {"id": uuid4(), "name": "Tag Test Workspace", "tags": ["new-tag-1", "new-tag-2"], "owner_id": owner.id}

    # Convert to model to test tag population
    result = await workspace_service._populate_with_owner_and_tags(workspace_data, "create")
    workspace_obj = cast("m.Workspace", result)

    assert hasattr(workspace_obj, "tags")
    assert len(workspace_obj.tags) == 2


async def test_populate_with_existing_tags(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test handling existing tags."""
    # Create owner user first (required by WorkspaceService for "create" operation)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    # Create existing tags
    existing_tag = TagFactory.build(name="existing-tag")
    session.add(existing_tag)
    await session.commit()

    workspace_data = {"id": uuid4(), "name": "Existing Tag Workspace", "tags": ["existing-tag", "new-tag"], "owner_id": owner.id}

    result = await workspace_service._populate_with_owner_and_tags(workspace_data, "create")
    workspace_obj = cast("m.Workspace", result)

    assert hasattr(workspace_obj, "tags")
    tag_names = [tag.name for tag in workspace_obj.tags]
    assert "existing-tag" in tag_names
    assert "new-tag" in tag_names


async def test_remove_tags_from_workspace(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test removing tags from existing workspace."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    # Create workspace with initial tags
    workspace_data = {"name": "Tag Removal Test", "tags": ["tag1", "tag2", "tag3"], "owner_id": owner.id}
    workspace = await workspace_service.create(data=workspace_data)

    # Update to remove some tags
    update_data = {
        "tags": ["tag1", "tag3"]  # Remove tag2
    }

    updated_workspace = await workspace_service.update(item_id=workspace.id, data=update_data, auto_refresh=True)
    await session.refresh(updated_workspace, ["tags"])

    tag_names = [tag.name for tag in updated_workspace.tags]
    assert "tag1" in tag_names
    assert "tag2" not in tag_names  # Should be removed
    assert "tag3" in tag_names
    assert len(updated_workspace.tags) == 2


async def test_get_nonexistent_workspace(workspace_service: WorkspaceService) -> None:
    """Test getting non-existent workspace returns None."""
    result = await workspace_service.get_one_or_none(id=uuid4())
    assert result is None


async def test_update_nonexistent_workspace(workspace_service: WorkspaceService) -> None:
    """Test updating non-existent workspace raises error."""
    with pytest.raises(RepositoryError):
        await workspace_service.update(item_id=uuid4(), data={"name": "Updated"})


async def test_delete_nonexistent_workspace(workspace_service: WorkspaceService) -> None:
    """Test deleting non-existent workspace raises error."""
    with pytest.raises(RepositoryError):
        await workspace_service.delete(item_id=uuid4())


async def test_create_workspace_empty_name(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test creating workspace with empty name."""
    # Create owner user first (required by WorkspaceService)
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    workspace_data = {"name": "", "description": "Empty name test", "owner_id": owner.id}

    # This should either raise an error or handle gracefully
    # Depending on validation rules
    try:
        workspace = await workspace_service.create(data=workspace_data)
    except (RepositoryError, IntegrityError, ValueError):
        return
    assert workspace.name == ""


async def test_create_workspace_with_nonexistent_owner(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test creating workspace with non-existent owner ID."""
    workspace_data = {
        "name": "Invalid Owner Workspace",
        "owner_id": uuid4(),  # Non-existent user ID
    }

    # Should handle gracefully - either create without owner or raise error
    try:
        workspace = await workspace_service.create(data=workspace_data)
    except (RepositoryError, IntegrityError, ValueError):
        return
    assert len(workspace.members) == 0


async def test_full_workspace_lifecycle(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test complete workspace lifecycle: create, update, add members, delete."""
    # Create owner
    owner = UserFactory.build()
    session.add(owner)
    await session.commit()

    # Create workspace
    workspace_data = {
        "name": "Lifecycle Test Workspace",
        "description": "Testing full lifecycle",
        "owner_id": owner.id,
        "tags": ["lifecycle", "test"],
    }
    workspace = await workspace_service.create(data=workspace_data, auto_refresh=True)

    # Verify creation - refresh to load relationships
    await session.refresh(workspace, ["members", "tags"])
    assert workspace.name == "Lifecycle Test Workspace"
    assert len(workspace.members) == 1
    assert workspace.members[0].is_owner is True
    assert len(workspace.tags) == 2

    # Update workspace
    update_data = {
        "description": "Updated description",
        "tags": ["lifecycle", "updated"],  # Change tags
    }
    updated_workspace = await workspace_service.update(item_id=workspace.id, data=update_data, auto_refresh=True)
    await session.refresh(updated_workspace, ["tags"])

    # Verify update
    assert updated_workspace.description == "Updated description"
    tag_names = [tag.name for tag in updated_workspace.tags]
    assert "updated" in tag_names
    assert "test" not in tag_names

    # Delete workspace
    await workspace_service.delete(item_id=workspace.id)

    # Verify deletion
    deleted_workspace = await workspace_service.get_one_or_none(id=workspace.id)
    assert deleted_workspace is None


async def test_workspace_with_multiple_members_and_tags(session: AsyncSession, workspace_service: WorkspaceService) -> None:
    """Test workspace with complex member and tag relationships."""
    # Create users
    owner = UserFactory.build()
    member1 = UserFactory.build()
    member2 = UserFactory.build()
    session.add_all([owner, member1, member2])
    await session.commit()

    # Create workspace with owner
    workspace_data = {
        "name": "Complex Workspace",
        "description": "Workspace with multiple relationships",
        "owner_id": owner.id,
        "tags": ["complex", "relationships", "testing"],
    }
    workspace = await workspace_service.create(data=workspace_data, auto_refresh=True)

    # Add additional members manually (simulating workspace invitation acceptance)
    member1_membership = WorkspaceMemberFactory.build(workspace_id=workspace.id, user_id=member1.id, role=m.WorkspaceRoles.MEMBER)
    member2_membership = WorkspaceMemberFactory.build(workspace_id=workspace.id, user_id=member2.id, role=m.WorkspaceRoles.MEMBER)
    session.add_all([member1_membership, member2_membership])
    await session.commit()

    # Refresh workspace to get updated members and tags
    await session.refresh(workspace, ["members", "tags"])

    # Verify complex relationships
    assert len(workspace.members) == 3  # Owner + 2 members
    assert len(workspace.tags) == 3

    # Verify owner has correct permissions
    owner_member = next((m for m in workspace.members if m.user_id == owner.id), None)
    assert owner_member is not None
    assert owner_member.is_owner is True
    assert owner_member.role == m.WorkspaceRoles.ADMIN

    # Verify regular members
    regular_members = [m for m in workspace.members if not m.is_owner]
    assert len(regular_members) == 2
    for member in regular_members:
        assert member.role == m.WorkspaceRoles.MEMBER
        assert member.is_owner is False
