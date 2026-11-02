import { computed } from "vue"
import { setAccessToken } from "#shared/api/config"
import { accountLogin, accountLogout, accountProfile } from "#shared/api/sdk.gen"
import type { Team, User } from "#shared/api/types.gen"
import { apiErrorMessage, unwrapAs } from "./api"

/**
 * Toast helper — Nuxt UI's `useToast().add()` wrapped in a sonner-like API so
 * the ported call sites read like the React app's `toast.error/success`.
 */
const useToaster = () => {
  const { add } = useToast()
  return {
    error: (message: string, opts?: { description?: string }) => add({ title: message, description: opts?.description, color: "error", icon: "i-lucide-circle-alert" }),
    success: (message: string, opts?: { description?: string }) => add({ title: message, description: opts?.description, color: "success", icon: "i-lucide-circle-check" }),
  }
}

/**
 * Auth state — Nuxt port of the React app's zustand `useAuthStore`
 * (`src/lib/auth.ts`), same behaviors:
 * - `login` handles the MFA-required response shape and verifies with profile
 * - `completeMfaLogin` finishes MFA flows with the MFA-issued access token
 * - `logout` clears token + state
 * - `checkAuth` re-verifies the session via the profile endpoint
 * - team state keeps `currentTeam` only while it remains in `teams`
 *
 * SPA mode: state lives in `useState` (app singleton) and the access token in
 * localStorage, mirroring the React app. When SSR is adopted, persist via a
 * cookie instead.
 */
export const useAuth = () => {
  const toast = useToaster()
  const userState = useState<User | null>("auth:user", () => null)
  const currentTeamState = useState<Team | null>("auth:currentTeam", () => null)
  const teamsState = useState<Team[]>("auth:teams", () => [])
  const isLoadingState = useState<boolean>("auth:isLoading", () => false)
  const isAuthenticatedState = useState<boolean>("auth:isAuthenticated", () => false)

  const patch = (values: Partial<{ user: User | null; currentTeam: null | Team; teams: Team[]; isLoading: boolean; isAuthenticated: boolean }>) => {
    if ("user" in values) userState.value = values.user
    if ("currentTeam" in values) currentTeamState.value = values.currentTeam
    if ("teams" in values) teamsState.value = values.teams
    if ("isLoading" in values) isLoadingState.value = values.isLoading
    if ("isAuthenticated" in values) isAuthenticatedState.value = values.isAuthenticated
  }

  const login = async (email: string, password: string): Promise<{ mfaRequired: boolean }> => {
    patch({ isLoading: true })
    try {
      const loginData = await unwrapAs<unknown, unknown, { access_token?: string; mfaRequired?: boolean }>(accountLogin({ body: { username: email, password } }))

      if (loginData?.mfaRequired) {
        setAccessToken(null)
        patch({ user: null, currentTeam: null, isAuthenticated: false })
        return { mfaRequired: true }
      }

      if (loginData?.access_token) {
        setAccessToken(loginData.access_token)
      }

      // Small delay to ensure the session cookie is set before verifying.
      await new Promise((resolve) => setTimeout(resolve, 100))

      // Verify the authentication by getting the profile.
      const profile = await unwrapAs<unknown, unknown, User>(accountProfile())
      patch({ user: profile, isAuthenticated: true })
      return { mfaRequired: false }
    } catch (error) {
      setAccessToken(null)
      patch({ user: null, currentTeam: null, isAuthenticated: false })
      toast.error(apiErrorMessage(error) || "Login failed")
      return { mfaRequired: false }
    } finally {
      patch({ isLoading: false })
    }
  }

  const completeMfaLogin = async (accessToken: string): Promise<void> => {
    patch({ isLoading: true })
    try {
      setAccessToken(accessToken)
      const profile = await unwrapAs<unknown, unknown, User>(accountProfile())
      patch({ user: profile, isAuthenticated: true })
    } catch (error) {
      setAccessToken(null)
      patch({ user: null, currentTeam: null, isAuthenticated: false })
      toast.error("MFA verification failed", { description: apiErrorMessage(error) || "Unable to complete login" })
    } finally {
      patch({ isLoading: false })
    }
  }

  const logout = async (): Promise<void> => {
    patch({ isLoading: true })
    try {
      await accountLogout()
    } finally {
      setAccessToken(null)
      patch({ user: null, currentTeam: null, isAuthenticated: false, isLoading: false })
    }
  }

  const checkAuth = async (): Promise<void> => {
    patch({ isLoading: true })
    try {
      const profile = await unwrapAs<unknown, unknown, User>(accountProfile())
      patch({ user: profile, isAuthenticated: true })
    } catch {
      setAccessToken(null)
      patch({ user: null, currentTeam: null, isAuthenticated: false })
    } finally {
      patch({ isLoading: false })
    }
  }

  const setCurrentTeam = (team: Team) => patch({ currentTeam: team })

  const setTeams = (newTeams: Team[]) => {
    const current = currentTeamState.value
    const nextCurrent = current && newTeams.some((team) => team.id === current.id) ? current : (newTeams[0] ?? null)
    patch({ teams: newTeams, currentTeam: nextCurrent })
  }

  return {
    user: computed(() => userState.value),
    currentTeam: computed(() => currentTeamState.value),
    teams: computed(() => teamsState.value),
    isLoading: computed(() => isLoadingState.value),
    isAuthenticated: computed(() => isAuthenticatedState.value),
    login,
    completeMfaLogin,
    logout,
    checkAuth,
    setCurrentTeam,
    setTeams,
  }
}
