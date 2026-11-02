# Cross-cutting infrastructure

Shared libraries used by every domain: email delivery, password/MFA cryptography, logging, validation, and server utilities. Structure and composition are described by `[[architecture]]`.

## Email

`[[src/py/app/lib/email/service.py#AppEmailService]]` renders Jinja/maizzle-compiled HTML templates (built from `[[src/js/templates/build-emails.ts]]`).

It sends signup, verification, password-reset, and invitation emails through the litestar-email `EmailService`. The mailer instance is provided as the `app_mailer` dependency by ApplicationCore.

## Cryptography

`[[src/py/app/lib/crypt.py]]` provides password hashing (pwdlib) plus the TOTP/QR/backup-code helpers used by `[[auth#MFA (TOTP)]]`.

## Settings

Everything tunable flows from `[[architecture#Configuration]]`; settings classes include `[[src/py/app/lib/settings.py#DatabaseSettings]]`, `[[src/py/app/lib/settings.py#AppSettings]]`, `[[src/py/app/lib/settings.py#EmailSettings]]`, `[[src/py/app/lib/settings.py#SaqSettings]]`, and `[[src/py/app/lib/settings.py#LogSettings]]`.

## Domain plugin utilities

The auto-discovery machinery (`[[architecture#Domain auto-discovery]]`) is composed of `[[src/py/app/utils/domain/_discovery.py]]` (module scanning), `[[src/py/app/utils/domain/_config.py#DomainPluginConfig]]` (toggles), and `[[src/py/app/utils/domain/_state.py]]` (cached discovery state).

## OAuth utilities

`[[src/py/app/utils/oauth.py#OAuth2ProviderPlugin]]` registers configured social providers; `[[src/py/app/utils/oauth.py#OAuth2AuthorizeCallback]]` handles the authorize-callback handshake, `[[src/py/app/utils/oauth.py#create_oauth_state]]`/`[[src/py/app/utils/oauth.py#verify_oauth_state]]` implement CSRF-style state protection.

## Serialization & DTOs

`[[src/py/app/utils/serialization.py#to_dict]]` and `[[src/py/app/utils/dto.py]]` handle msgspec serialization helpers used across controllers and services.