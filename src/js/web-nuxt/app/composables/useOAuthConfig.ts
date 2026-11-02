import { oAuthConfig } from "#shared/api/sdk.gen"
import type { OAuthConfigResponses } from "#shared/api/types.gen"
import { unwrap } from "./api"

/**
 * Nuxt port of the React app's `hooks/use-oauth-config.ts`.
 * Shared OAuth config state — single fetch, cached for the app lifetime
 * (mirrors staleTime 5 min + retry false; in Nuxt a module-level cache is fine
 * for a client-only SPA).
 */
const configState = useState<OAuthConfigResponses | null>("oauth-config", () => null)
let fetching: Promise<OAuthConfigResponses | null> | null = null

const DEFAULT_CONFIG: OAuthConfigResponses = {
  googleEnabled: false,
  githubEnabled: false,
}

export const useOAuthConfig = () => {
  if (import.meta.client && !configState.value && !fetching) {
    fetching = (async () => {
      try {
        const data = await unwrap<OAuthConfigResponses, unknown>(oAuthConfig({ security: [] }))
        configState.value = data ?? DEFAULT_CONFIG
        return configState.value
      } catch {
        configState.value = DEFAULT_CONFIG
        return DEFAULT_CONFIG
      } finally {
        fetching = null
      }
    })()
  }

  return computed(() => configState.value ?? DEFAULT_CONFIG)
}
