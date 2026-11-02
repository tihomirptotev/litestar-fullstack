# Email Templates: React → Vue (Maizzle) Migration Plan

> Plan for replacing the react-email templates in `src/js/templates/` with
> Vue-based templates rendered by [Maizzle](https://maizzle.com).
> Status: **planned, not executed**. Companion doc: `docs/nuxt-migration-plan.md`.

## 1. What `src/js/templates/` is today

It is **not an app** — it's the **react-email email-template build package** (~815 lines):

| File | Role |
|---|---|
| `src/components/{Layout,Header,Footer,Button}.tsx` | Shared email chrome (navy/gold brand theme) |
| `src/emails/*.tsx` | 5 templates: `email-verification`, `welcome`, `password-reset`, `password-reset-confirmation`, `team-invitation` |
| `src/lib/theme.ts` | Plain TS design tokens (no React — reusable as-is) |
| `build-emails.ts` | Bun script: dynamic-imports each TSX, `render()`s to static HTML → writes to `src/py/app/server/static/email/` |
| `package.json` | Bun runtime, `react`, `react-dom`, `@react-email/components`, `@react-email/render` |

### The consumer contract (must not change)

`src/py/app/lib/email/service.py` loads the built `*.html` files and does naive
`str.replace("{{KEY}}", value)` on placeholders:

- `{{APP_NAME}}` (always injected)
- `{{USER_NAME}}`, `{{VERIFICATION_URL}}`, `{{EXPIRES_HOURS}}` (email-verification)
- `{{LOGIN_URL}}` (welcome, password-reset-confirmation)
- `{{RESET_URL}}` (password-reset)
- `{{TEAM_NAME}}`, `{{INVITER_NAME}}`, `{{INVITATION_URL}}` (team-invitation)

The Python side stays **untouched**. The output of the new build must contain
these `{{PLACEHOLDER}}` strings **literally** in the HTML.

## 2. Tooling choice: Maizzle

Per https://maizzle.com/docs/migrate/react-email :

- **Vue-based** (satisfies "Nuxt/Vue" for this package) and actively maintained —
  unlike `@vue-email/*` (quiet since its 2024 rewrite) and its fork `vuemailer`.
- **~100% component parity with react-email** (`Html`, `Head`, `Body`,
  `Container`, `Section`, `Heading`, `Text`, `Button`; `Preview` → `Preheader`).
- **`<Raw>` component** solves the mustache collision for free: literal
  `{{PLACEHOLDER}}` delimiters pass through untouched, exactly what ESP-style
  templating needs. Vanilla Vue would eat them; Maizzle's `Raw` emits them
  verbatim. (Fallback for single attribute values: `v-pre` or HTML entities.)
- `render()` from `@maizzle/framework` runs the full pipeline (SSR, CSS
  inlining, transformers, doctype) and returns `{ html, plaintext? }`.
- `style` objects can stay as `:style` objects — no need to convert to
  Tailwind (Tailwind is available but optional).

## 3. Phases

### Phase 1 — Scaffold (swap the runtime)

- New standard Maizzle project layout inside `src/js/templates/`:
  `src/components/`, `src/templates/` (our 5 emails), `src/layouts/`, `config.ts`.
- `package.json`: drop `react`, `react-dom`, `@types/react`, `@react-email/*`;
  add `@maizzle/framework`. Runtime moves from Bun to Node (`maizzle build`).

### Phase 2 — Port shared components to SFCs

- `Layout.vue` (rename ours → `EmailLayout`, **name collision alert** with
  Maizzle's built-in `<Layout>` skeleton), `Header.vue`, `Footer.vue`, `Button.vue`.
- `variant?: "primary" | "success" | "secondary"` prop maps directly.
- `src/lib/theme.ts` unchanged (pure TS tokens imported by the SFCs).

### Phase 3 — Port the 5 email templates to SFCs

- Mechanical `.tsx` → `.vue` translation (97–119 lines each):
  - every literal placeholder → `<Raw>{{APP_NAME}}</Raw>` etc.
  - `Preview` → `Preheader`
  - `style` objects → `:style` bindings (unchanged values)

### Phase 4 — Build step

- `build-emails.ts` is mostly **deleted**: configure Maizzle's
  `build.output_dir` → `src/py/app/server/static/email/` with identical
  filenames; `--watch` replaced by `maizzle dev`.
- Preserve behaviors: skip `_`-prefixed files, pretty output, global CSS
  inlining hook, per-file success/fail logging, exit 1 on failures.

### Phase 5 — Verify parity (acceptance gate)

- Build both old (React) and new (Maizzle) versions once; diff the 5 HTML
  outputs. Expected acceptable deltas: attribute order, wrapper markup
  minutiae. **Hard requirements** (scripted check, not eyeballed):
  - all `{{PLACEHOLDER}}` strings present **literally**
  - no Vue SSR artifacts (no interpolation residue, no `data-v-` attrs,
    no `<!--[--->` fragments)
  - email-safe: inline styles, `<Preheader>` present, `word-break: break-all`
    link boxes intact
- Run the real consumer: call `_render_template` in a Python test (or boot the
  app and trigger a verification email), confirm placeholders substitute.

### Phase 6 — Cleanup

- Delete `.tsx` sources + `src/components/index.ts`, regen lockfile, remove
  React deps.
- Update docs referencing react-email.
- Optional: fold the build into `tools/post_builds.py` / CI so templates
  rebuild with the wheel.

## 4. Risks / open questions

1. **Keep the React version until Phase 5 passes** — delete only after the
   diff gate is green; makes the migration reversible at any point.
2. **Curly-brace placeholders** are the #1 silent-failure mode (empty
   placeholders in production emails) — hence the scripted Phase 5 check.
3. **Idiomatic-vs-1:1 port**: keep shared `Header`/`Footer`/`Button` components
   for the closest port; refactoring to Maizzle's `<Layout>`-based skeleton is
   a possible later cleanup, not part of the gate.
4. **Node vs Bun**: Maizzle targets Node; the output is static HTML either
   way, so the runtime swap has no effect on email sending.
5. **Bonuses available later** (not in scope): `plaintext: true` free text
   alternatives; Maizzle dev server for live preview.

## 5. Estimate

~450 lines of Vue + a thin build config replacing ~700 lines of TSX and the
96-line `build-emails.ts` — one focused sitting for Phases 1–4 plus a
verification pass.