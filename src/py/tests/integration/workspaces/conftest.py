"""Workspace domain integration test fixtures.

These fixtures provide service instances for workspace-related tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.db import models as m
from app.domain.tags.services import TagService
from app.domain.workspaces.services import WorkspaceInvitationService, WorkspaceMemberService, WorkspaceService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.anyio


@pytest.fixture
async def workspace_service(session: AsyncSession) -> AsyncGenerator[WorkspaceService, None]:
    """Create WorkspaceService instance with test session."""
    async with WorkspaceService.new(session, load=[m.Workspace.tags, m.Workspace.members]) as service:
        yield service


@pytest.fixture
async def workspace_member_service(session: AsyncSession) -> AsyncGenerator[WorkspaceMemberService, None]:
    """Create WorkspaceMemberService instance."""
    async with WorkspaceMemberService.new(session) as service:
        yield service


@pytest.fixture
async def workspace_invitation_service(session: AsyncSession) -> AsyncGenerator[WorkspaceInvitationService, None]:
    """Create WorkspaceInvitationService instance."""
    async with WorkspaceInvitationService.new(session) as service:
        yield service


@pytest.fixture
async def tag_service(session: AsyncSession) -> AsyncGenerator[TagService, None]:
    """Create TagService instance."""
    async with TagService.new(session) as service:
        yield service
