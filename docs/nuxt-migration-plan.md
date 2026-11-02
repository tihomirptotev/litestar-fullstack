# Rewrite Plan: React SPA → Nuxt 4 + Nuxt UI v4

> Plan for rewriting `src/js/web/` (React 19 + TanStack Router/Query + shadcn/ui SPA)
> using **Nuxt 4** + **Nuxt UI v4** (`@nuxt/ui`), preserving all current behavior.
> Status: planning only — no code written yet.

## Current State (`src/js/`)

**`src/js/web/` — React 19 SPA** ("litestar-fullstack-spa"), served by a Litestar (Python) backend:

- **TanStack Router** file-based routes: pathless layouts `_app` (auth-guarded) and
  `_public`, with auth/teams/admin/profile surfaces, OAuth callbacks, MFA challenge,
  404 splat route.
- **TanStack Query** + **@hey-api/openapi-ts** generated SDK (client, types,
  react-query hooks) from the Litestar OpenAPI schema; silent token-refresh
  interceptor queue in `src/js/web/src/main.tsx`.
- **Zustand** `useAuthStore` (persisted) holding user/isAuthenticated;
  **react-hook-form** + **zod** for forms; **sonner** toasts; custom ThemeProvider.
- **shadcn/ui** components on Radix (incl. a 584-line custom `sidebar.tsx`),
  Tailwind CSS v4, lucide icons, framer-motion.
- Built via Vite + `litestar-vite-plugin` in SPA mode → bundles into
  `src/py/app/server/static/web/`; CSRF token injected via
  `window.__LITESTAR_CSRF__`; bearer token in `localStorage`.

**`src/js/templates/` — React Email** templates compiled by Bun to static HTML for
the backend. Independent of the SPA — out of scope for this rewrite (optional
later port to Vue Email).

## Phases

### Phase 0 — Scaffold & architecture decisions

1. New app at `src/js/web-nuxt/` (keep old app until parity): `npx nuxi init`,
   `@nuxt/ui` + `tailwindcss`, `UApp` wrapper, `app/assets/css/main.css` with
   `@import "tailwindcss"; @import "@nuxt/ui"`.
2. **Rendering mode: start with `ssr: false` (SPA)** to preserve current behavior
   (auth headers, localStorage token, backend serving static). Later optionally
   move to hybrid/SSR via `routeRules` — but SSR requires moving the access token
   out of `localStorage` into an httpOnly cookie (decision point).
3. **Dev workflow**: replace `litestar-vite-plugin` (React/Vite-specific) with
   `nitro.devProxy` proxying `/api` → `http://127.0.0.1:8000`. Production build
   output → backend static dir, as today.
4. Keep Bun as executor and keep Biome for lint/format (drop Prettier/eslint).

### Phase 1 — API layer (replace TanStack Query)

- Keep `@hey-api/openapi-ts` codegen (framework-agnostic) but regenerate
  **without** the `@tanstack/react-query` plugin — SDK functions only.
- Wrap SDK calls in composables using `useAsyncData`/`useFetch` (SPA-safe,
  handles loading/error states); plain mutations via SDK functions.
- Recreate the client config: `credentials: "include"`, bearer token getter,
  CSRF header injection (`window.__LITESTAR_CSRF__`), and the **silent 401
  refresh queue** as a custom `$fetch` instance (`$api`) with interceptors.

### Phase 2 — Auth & state (replace Zustand)

- `app/composables/useAuth.ts` backed by `useState()` (+ Pinia store with cookie
  persistence once SSR-ready) — or start with `useState` + localStorage in SPA
  mode to mirror current behavior exactly.
- Port: `login`, `completeMfaLogin`, `logout`, `checkAuth`, teams/current-team state.
- **Route middleware** replaces the `_app` layout guard: `app/middleware/auth.ts`
  doing the same check-then-verify logic with
  `navigateTo({ path: '/login', query: { redirect } })`. Public pages need no guard.
- Keep `getSafeRedirectUrl` (open-redirect protection) and zod validation schemas
  (`lib/validation.ts`) — zod works as-is with Nuxt UI forms.

### Phase 3 — Routing map

| Current (TanStack) | Nuxt 4 |
|---|---|
| `routes/__root.tsx` | `app/app.vue` (`UApp` + `NuxtPage`) + `layouts/` |
| `routes/_app.tsx` + `AppLayout` | `layouts/app.vue` + `middleware/auth.ts` |
| `routes/_public.tsx` + `PublicLayout` | `layouts/public.vue` |
| `routes/_public/landing.tsx`, `login.tsx` … | `app/pages/landing.vue`, `login.vue` … |
| `routes/_app/teams/$teamId.tsx` | `app/pages/teams/[teamId].vue` |
| `routes/_app/admin/teams/index.tsx` | `app/pages/admin/teams/index.vue` |
| `routes/$.tsx` (404) | `error.vue` / catch-all page |
| `validateSearch` (zod search params) | `definePageMeta` + typed `useRoute().query` validation in page `setup` |
| OAuth callbacks (`?token&is_new&error`) | `app/pages/auth/google/callback.vue` etc., same query handling |

### Phase 4 — UI components (shadcn/Radix → Nuxt UI v4)

Follow the nuxt-ui dashboard layout recipe:

- **Dashboard sidebar**: `UDashboardSidebar`/`UNavigationMenu` — replaces the
  584-line custom sidebar, `nav-main`, `nav-projects`, `team-switcher`
  (`UDashboardPanel` + `USelect` for team switching), `nav-user`/`user-menu`
  (`UDropdownMenu`).
- Component mapping:

  | shadcn/ui | Nuxt UI v4 |
  |---|---|
  | `button` | `UButton` |
  | `card` | `UCard` |
  | `dialog` / `sheet` | `UModal` / `USlideover` |
  | `form` (react-hook-form) | `UForm` + `UFormField` with zod (Standard Schema) |
  | `data-table` / `table` | `UTable` (built on TanStack Table — direct port) |
  | `select` | `USelect` / `USelectMenu` |
  | `tabs` | `UTabs` |
  | `dropdown-menu` | `UDropdownMenu` |
  | `tooltip` | `UTooltip` |
  | `sonner` toasts | `useToast()` via `UApp` |
  | `skeleton` | `USkeleton` |
  | `alert` | `UAlert` |
  | `avatar` | `UAvatar` |
  | `badge` | `UBadge` |
  | `breadcrumb` | `UBreadcrumbs` |
  | `separator` | `USeparator` |
  | `collapsible` | `UCollapsible` |

- **Custom keepers** (no Nuxt UI equivalent — port as-is): `totp-input`,
  `password-strength`, `retro-grid`, `auth-hero-panel`, `motion.tsx`
  (framer-motion → `@vueuse/motion` or CSS transitions).
  Delete thin wrappers `validated-form`/`validated-input` in favor of `UForm`.
- **Theme**: drop `theme-context.tsx` + `theme-toggle`; use Nuxt UI's built-in
  dark mode (`@nuxtjs/color-mode` included via `@nuxt/ui`). Map existing brand
  palette (navy, gold `edb641`) into `app/app.config.ts` `ui.colors` + `main.css`
  semantic tokens.
- Icons: `lucide-react` → `i-lucide-*` via Nuxt UI's Iconify integration.

### Phase 5 — Pages (port order)

1. **Auth cluster**: login, signup, forgot/reset-password, verify-email,
   mfa-challenge, both OAuth callbacks — highest-risk logic (token handling,
   MFA, redirects).
2. **Landing + static pages**: landing, about, privacy, terms.
3. **App shell**: layout, sidebar, user menu, team switcher.
4. **Teams**: list, `[teamId]`, new, invitation accept.
5. **Profile**: MFA setup/disable dialogs, backup codes, connected accounts,
   OAuth link buttons.
6. **Admin**: dashboard stats cards, user table, team table, audit log table
   (`UTable` + data-tables recipe: filters, pagination, sorting).

### Phase 6 — Testing & quality

- Vitest + `@nuxt/test-utils` + `@vue/test-utils` replaces the current RTL setup;
  port the existing `mfa-disable-dialog.test.tsx` pattern to component tests.
- Keep Biome config, adapt path alias `@` → `~`/`@` (Nuxt `app/` alias).

## Out of Scope / Deferred

- `src/js/templates/` email build — leave as React Email (compiles to static HTML
  independently). Optional later port to Vue Email.
- Full SSR — requires cookie-based session (httpOnly cookie instead of
  localStorage bearer token); follow-up after SPA parity.

## Risks & Decision Points

1. **`litestar-vite-plugin` has no Nuxt equivalent** — dev proxy + build output
   config must be hand-rolled; CSRF injection mechanism
   (`window.__LITESTAR_CSRF__`) needs verification against how the plugin injects
   it (it hooks Vite's transform pipeline).
2. **localStorage bearer token + SSR are incompatible** — if SSR is wanted later,
   the backend should set an httpOnly cookie; decide during Phase 0.
3. **Silent refresh queue** logic is subtle (failed-request queuing,
   public-page loop guards) — port carefully with tests.
4. Admin route naming is case-sensitive in Nuxt — all lowercase already, no
   issues expected.