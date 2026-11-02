This directory defines the high-level concepts, business logic, and architecture of this project using markdown. It is managed by [lat.md](https://www.npmjs.com/package/lat.md) — a tool that anchors source code to these definitions. Install the `lat` command with `npm i -g lat.md` and run `lat --help`.

- [[architecture]] — layered Litestar app: config → plugins → ApplicationCore → auto-discovered domains
- [[auth]] — JWT OAuth2 auth, refresh tokens, MFA (TOTP), email verification, password reset, social OAuth
- [[domains]] — feature domains: accounts, workspaces, admin, tags, system; SQLAlchemy models
- [[infrastructure]] — cross-cutting libs: email, cryptography/MFA helpers, settings, discovery utils, OAuth utilities
- [[tests]] — test specifications for auth routes (login)