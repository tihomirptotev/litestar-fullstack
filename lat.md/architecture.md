# Architecture

Litestar Fullstack is a production-oriented reference web application with a layered, plugin-driven design: configuration feeds server plugins, plugins assemble the ASGI app, and a self-discovering domain layer supplies routes and services.

Everything below `[[src/py/app]]` runs from a single `[[src/py/app/__main__.py]]` CLI entry point.

## Request lifecycle

An incoming request flows through Granian -> Litestar -> guards -> dependencies -> controllers -> services -> repositories, with exceptions translated to problem-details responses.

The application is created by `[[src/py/app/server/asgi.py#create_app]]`, which instantiates Litestar with the single `[[src/py/app/server/core.py#ApplicationCore]]` plugin. `ApplicationCore.on_app_init` is the composition root: it wires OpenAPI/security, CORS, the SPA static router, plugin list, signature namespace, exception handlers, and core dependencies (`current_user`, `settings`, `app_mailer`).

## Plugin stack

Server plugins live in `[[src/py/app/server/plugins.py]]` and are registered by ApplicationCore.

They are: structlog (logging), SQLAlchemy via Advanced Alchemy, Granian (ASGI server), SAQ (background jobs), problem-details errors, the custom OAuth2 provider plugin, email, and the domain-discovery plugin.

## Domain auto-discovery

`[[src/py/app/utils/domain/_plugin.py#DomainPlugin]]` scans `app.domain.*` packages at startup.

It registers Controller classes, event listeners, and signature-namespace entries for schemas, services, and repositories — so new domain modules are picked up without manual route tables. The scanning logic itself is in `[[src/py/app/utils/domain/_discovery.py]]`.

## Configuration

`[[src/py/app/lib/settings.py#Settings]]` is a dataclass aggregate (app, db, server, saq, log, email) loaded once from environment/`.env` via `[[src/py/app/lib/settings.py#get_settings]]`.

`[[src/py/app/config.py]]` derives the concrete plugin configs (compression, cors, alchemy, problem details, logging, email, SAQ) from settings at import time; SAQ config is lazy to avoid a Redis connection during build.

## Dependency injection

`[[src/py/app/lib/deps.py]]` builds Service/Repository providers from Advanced Alchemy helpers.

`provide_services` composes session-bound services (with `CompositeServiceMixin` for shared multi-service sessions), and filter dependencies power list pagination. Controllers typically take services as DI parameters.

## Repository & service pattern

All persistence goes through Advanced Alchemy's `SQLAlchemyAsyncRepositoryService` / `SQLAlchemyAsyncRepository` pairs (e.g. `[[src/py/app/domain/accounts/services/_user.py#UserService]]`). `[[src/py/app/lib/service.py#AutoSlugServiceMixin]]` auto-populates slug fields from names on create/update/upsert.

## Background jobs

SAQ workers run domain jobs such as `[[src/py/app/domain/accounts/jobs/_oauth_refresh.py#refresh_oauth_tokens]]`; worker-side logging utilities live in `[[src/py/app/lib/worker.py#before_process_job]]`.

## CLI

`[[src/py/app/cli/commands.py#user_management_group]]` adds database fixtures, user creation, superuser promotion, and default-role seeding to the `app` CLI (installed as `app = app.__main__:run_cli`).

## Exception handling

Domain errors extend `[[src/py/app/lib/exceptions.py#ApplicationError]]` and are mapped to HTTP responses (problem details) by handlers registered in ApplicationCore, alongside `RepositoryError`/`DuplicateKeyError` and validation errors.