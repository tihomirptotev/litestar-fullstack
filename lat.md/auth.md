# Authentication & MFA

Authentication is OAuth2 bearer JWT issued at `/api/access/login`, backed by a 15-minute access token expiration and DB-persisted refresh tokens.

MFA (TOTP), email verification, password reset, and OAuth2 social login build on top of the same guard stack.

## JWT guard and access tokens

`[[src/py/app/domain/accounts/guards.py#auth]]` is an `OAuth2PasswordBearerAuth` whose `retrieve_user_handler` is `[[src/py/app/domain/accounts/guards.py#current_user_from_token]]` (loads the active user by token `sub`, the email).

Access tokens are minted by `[[src/py/app/domain/accounts/guards.py#create_access_token]]` with extras (user_id, is_superuser, is_verified, auth_method, amr). Public/excluded paths are listed in the guard's `exclude`.

## Guards

`requires_active_user`, `requires_verified_user`, and `requires_superuser` in `[[src/py/app/domain/accounts/guards.py]]` gate handlers via Litestar guards.

## Login, refresh, sessions

`[[src/py/app/domain/accounts/controllers/_access.py#AccessController]]` implements login/logout/refresh/signup/forgot-password/reset-password plus per-session listing and revocation. Refresh tokens are persisted and managed by `[[src/py/app/domain/accounts/services/_refresh_token.py#RefreshTokenService]]`.

## MFA (TOTP)

MFA schemas (setup/confirm/backup-codes/disable/challenge) are msgspec structs in `[[src/py/app/domain/accounts/schemas/_mfa.py]]`.

Crypto helpers in `[[src/py/app/lib/crypt.py]]` generate TOTP secrets, verify 6-digit codes, build provisioning URIs, render QR codes, and verify backup codes; the controllers live in `[[src/py/app/domain/accounts/controllers/_mfa.py]]` and `[[src/py/app/domain/accounts/controllers/_mfa_challenge.py]]`.

## OAuth2 social login

OAuth flows (GitHub/Google via httpx-oauth) are handled by `[[src/py/app/domain/accounts/controllers/_oauth.py]]` with state create/verify helpers from `[[src/py/app/utils/oauth.py#OAuth2AuthorizeCallback]]`; linked accounts are managed by `[[src/py/app/domain/accounts/services/_user_oauth_account.py#UserOAuthAccountService]]`. `[[src/py/app/domain/accounts/jobs/_oauth_refresh.py#refresh_oauth_tokens]]` refreshes expiring provider tokens on the SAQ queue.

## Email verification & password reset

`[[src/py/app/domain/accounts/services/_email_verification.py#EmailVerificationService]]` and `[[src/py/app/domain/accounts/services/_password_reset.py#PasswordResetService]]` issue tokens (models `_email_verification_token` / `_password_reset_token`) and are driven by controllers `_email_verification.py` and the AccessController reset endpoints. Password strength is checked by `[[src/py/app/lib/validation.py#validate_password_strength]]`.

## Constants

Default role names, superuser role, and related values live in `[[src/py/app/lib/constants.py]]`.