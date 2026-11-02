# Litestar Fullstack — Nuxt Frontend

Nuxt 4 + Nuxt UI v4 rewrite of the previous React SPA (`../web/`), served by the
Litestar backend. See `docs/nuxt-migration-plan.md` (repo root) for the full
migration plan.

## Current status: Phase 0 (scaffold)

- Nuxt 4.6.3 + `@nuxt/ui` v4, Tailwind CSS v4
- SPA mode (`ssr: false`) to match the React app's auth model (bearer token in
  `localStorage`, backend serves static bundle)
- Dev proxy: `/api` → `http://127.0.0.1:8000` (Litestar), configurable via
  `LITESTAR_URL`
- Biome for lint/format (same config style as `../web/`)

## Commands

```bash
npm install
npm run dev        # dev server (proxies /api to the Litestar backend)
npm run build      # production build (static SPA in .output/public)
npm run lint       # biome check --write
npm run typecheck  # nuxt typecheck
npm run test       # vitest
```

## Production

Build output is a static SPA under `.output/public/`. To serve it from the
Litestar backend (as the React app does), point the backend's static/Vite
config at this directory — to be wired up when the rewrite reaches parity.