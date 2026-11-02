import { validateRedirectUrl } from "~/utils/redirect-utils"

/**
 * Route middleware — Nuxt port of the React app's `_app.tsx` pathless layout
 * `beforeLoad` auth guard.
 *
 * Flow (same semantics):
 * 1. Fast path: access token in localStorage → allow (verification happens
 *    in the layout with checkAuth, like the React app).
 * 2. No token: checkAuth() (profile fetch) → on success allow with token set
 *    by the refresh cookie path; on 401 → redirect to /login?redirect=<here>
 * 3. Infinite-loop protection mirrors the React app's public-page checks.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuth()

  // Fast path — token present, trust it (layout re-verifies via checkAuth).
  // Uses raw localStorage read to avoid a circular dependency on the composable's
  // configured key name.
  if (import.meta.client && localStorage.getItem("access_token")) {
    return
  }

  // No token — verify the session cookie path.
  if (import.meta.client) {
    try {
      await auth.checkAuth()
    } catch {
      // handled below
    }

    if (!auth.isAuthenticated.value) {
      const redirectTo = to.fullPath && to.fullPath !== "/" ? to.fullPath : null
      const validated = validateRedirectUrl(redirectTo)
      return navigateTo(validated ? { path: "/login", query: { redirect: validated } } : "/login")
    }
  }
})
