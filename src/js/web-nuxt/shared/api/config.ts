import type { CreateClientConfig } from "./client.gen"
import { client } from "./client.gen"

/**
 * Auth client wiring for the generated hey-api client — mirrors the
 * React app's `src/main.tsx` setup:
 * - bearer access token from localStorage (SPA mode; move to httpOnly
 *   cookies if/when SSR is adopted)
 * - cookie credentials for the Litestar session
 * - silent 401 token refresh with request queuing
 */

const ACCESS_TOKEN_KEY = "access_token"

export const getAccessToken = (): string | null => {
  if (typeof window === "undefined") {
    return null
  }
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export const setAccessToken = (token: string | null) => {
  if (typeof window === "undefined") {
    return
  }
  if (token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, token)
  } else {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
  }
}

// Pages where a failed auth check should NOT trigger a refresh/redirect loop.
const PUBLIC_AUTH_PATHS = ["/login", "/signup", "/forgot-password", "/reset-password"]

const isPublicAuthPath = (): boolean => {
  if (typeof window === "undefined") {
    return false
  }
  const path = window.location.pathname
  return PUBLIC_AUTH_PATHS.some((p) => path.startsWith(p))
}

// ---------------------------------------------------------------------------
// Silent refresh queue
// ---------------------------------------------------------------------------

let isRefreshing = false
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason?: unknown) => void }> = []

const processQueue = (error: Error | null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve(undefined)
    }
  })
  failedQueue = []
}

export function configureClient({ baseUrl }: { baseUrl?: string } = {}) {
  client.setConfig({
    baseUrl: baseUrl ?? "",
    credentials: "include",
    auth: () => {
      if (typeof window === "undefined") {
        return undefined
      }
      return window.localStorage.getItem(ACCESS_TOKEN_KEY) ?? undefined
    },
  })

  // Silent token refresh — uses the error interceptor with the new client API.
  client.interceptors.error.use(async (error, response, request, options) => {
    // Only attempt refresh for 401 errors, not on the refresh/login endpoints
    const requestUrl = request?.url
    if (response?.status === 401 && !requestUrl?.includes("/api/access/refresh") && !requestUrl?.includes("/api/access/login")) {
      // Skip refresh attempt on public auth pages to prevent infinite loops
      if (isPublicAuthPath()) {
        throw error
      }

      if (isRefreshing) {
        // If already refreshing, queue this request
        await new Promise<void>((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
        // Retry the original request
        const method = options.method ?? "GET"
        return client.request({ ...options, method, url: requestUrl })
      }

      isRefreshing = true
      try {
        // Refresh the session cookie; the server returns a new access token.
        await client.post({ url: "/api/access/refresh" })
        processQueue(null)
        // Retry the original request
        const method = options.method ?? "GET"
        return client.request({ ...options, method, url: requestUrl })
      } catch (refreshError) {
        processQueue(refreshError as Error)
        if (typeof window !== "undefined" && window.location.pathname !== "/login") {
          window.location.href = "/login"
        }
        throw refreshError
      } finally {
        isRefreshing = false
      }
    }

    throw error
  })
}

export type { CreateClientConfig }
