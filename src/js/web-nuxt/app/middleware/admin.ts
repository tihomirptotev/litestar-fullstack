/**
 * Route middleware — Nuxt port of the React app's `routes/_app/admin.tsx`
 * layout guard: only superusers may browse `/admin/**`.
 *
 * Assumes the `auth` middleware already ran (layout-level), so the user is
 * loaded; a non-superuser is bounced to `/home`.
 */
export default defineNuxtRouteMiddleware(() => {
  const auth = useAuth()
  const user = auth.user.value
  if (!user?.isSuperuser) {
    return navigateTo("/home")
  }
})
