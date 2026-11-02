# Domains

The `app.domain` package is split into feature domains (accounts, workspaces, admin, tags, system), each with `controllers/`, `services/`, and `schemas/` subpackages discovered automatically by `[[architecture#Domain auto-discovery]]` — see `[[architecture]]` for how they are wired in.

## Accounts

Users, roles, auth surfaces, MFA, OAuth accounts, email verification, and password reset. See `[[auth]]` for the auth details. Core service: `[[src/py/app/domain/accounts/services/_user.py#UserService]]` (also handles password hashing via `app.lib.crypt`, OAuth composite access, and reset failure limits).

## Workspaces

Multi-tenant workspaces with membership, invitations, roles, and tags.

Workspace membership authorization is enforced by `[[src/py/app/domain/workspaces/guards.py#requires_workspace_membership]]` and admin checks by `[[src/py/app/domain/workspaces/guards.py#requires_workspace_admin]]` (system superusers bypass). Services: `_workspace.py`, `_workspace_member.py`, `_workspace_invitation.py` under `[[src/py/app/domain/workspaces/services]]`.

## Admin

Superuser dashboards: audit logs, user administration, workspace administration, and dashboard aggregates under `[[src/py/app/domain/admin]]`. Audit-trail writes are handled by `[[src/py/app/domain/admin/services/_audit.py#AuditLogService]]` and triggered from `[[src/py/app/db/models/_audit_log.py#AuditLogRecord]]` events via `[[src/py/app/domain/accounts/listeners.py]]`.

## Tags

Tag CRUD with slug auto-generation (uses `[[architecture#Repository & service pattern]]`): `[[src/py/app/domain/tags/services/_tag.py#TagService]]`.

## System

Health endpoints (`/health`, `/health/*`), schema, and maintenance jobs in `[[src/py/app/domain/system]]`; the DB/engine bootstrap used by health checks is `[[src/py/app/utils/engine_factory.py#create_engine]]`.

## Database models

SQLAlchemy models under `[[src/py/app/db/models]]` (User, Role, OAuthAccount, RefreshToken, tokens for verification/reset, Workspace + member/role/invitation/tag join models, AuditLogRecord, Tag) built on `UUIDv7AuditBase` with PII column tracking via `__pii_columns__`.