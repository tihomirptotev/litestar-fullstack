import { configureClient } from "../../shared/api/config"

/**
 * SPA bootstrap.
 *
 * - Applies auth/CSRF/silent-refresh interceptors to the hey-api client on
 *   app startup (client-side only — SPA mode).
 * - No SSR-specific logic yet; revisit when adopting SSR/httpOnly cookies.
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  configureClient({
    baseUrl: (config.public.apiBase as string) ?? "",
  })
})
