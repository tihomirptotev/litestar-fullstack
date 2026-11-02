"""Admin domain schemas."""

from app.domain.admin.schemas._audit import AuditLogEntry
from app.domain.admin.schemas._dashboard import ActivityLogEntry, DashboardStats, RecentActivity
from app.domain.admin.schemas._workspaces import AdminWorkspaceDetail, AdminWorkspaceSummary, AdminWorkspaceUpdate
from app.domain.admin.schemas._users import AdminUserDetail, AdminUserSummary, AdminUserUpdate

__all__ = (
    "ActivityLogEntry",
    "AdminWorkspaceDetail",
    "AdminWorkspaceSummary",
    "AdminWorkspaceUpdate",
    "AdminUserDetail",
    "AdminUserSummary",
    "AdminUserUpdate",
    "AuditLogEntry",
    "DashboardStats",
    "RecentActivity",
)
