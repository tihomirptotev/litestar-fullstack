<script setup lang="ts">
/**
 * OAuth callback — Nuxt port of the React app's
 * `routes/_public/auth/{google,github}/callback.tsx` (single shared page, the
 * provider only affects success-message wording and the sessionStorage key).
 *
 * Flow: read query params (token/is_new/error/message) → on error show error
 * card → on success store token, refetch user, show success card, then
 * redirect to the stored post-auth destination from sessionStorage.
 */
definePageMeta({ layout: false })

const route = useRoute()
const toast = useToast()
const auth = useAuth()

const provider = computed(() => (route.path.includes("/github/") ? "github" : "google"))

const REDIRECT_KEYS = {
  google: "google_auth_redirect",
  github: "github_auth_redirect",
} as const

const status = ref<"processing" | "error" | "success">("processing")
const errorMessage = ref<string | null>(null)

const handleCallback = async () => {
  const token = route.query.token as string | undefined
  const errorParam = route.query.error as string | undefined
  const message = route.query.message as string | undefined

  if (errorParam) {
    errorMessage.value =
      errorParam === "access_denied" ? `You denied access to your ${provider.value === "github" ? "GitHub" : "Google"} account` : `Authentication failed: ${errorParam}`
    status.value = "error"
    toast.add({ title: errorMessage.value, color: "error", icon: "i-lucide-circle-alert" })
    return
  }

  if (!token) {
    errorMessage.value = message || "Invalid OAuth callback - missing token"
    status.value = "error"
    toast.add({ title: errorMessage.value, color: "error", icon: "i-lucide-circle-alert" })
    return
  }

  localStorage.setItem("access_token", token)
  await auth.checkAuth()

  status.value = "success"
  toast.add({ title: `Successfully signed in with ${provider.value === "github" ? "GitHub" : "Google"}!`, color: "success", icon: "i-lucide-circle-check" })

  // Get and clear stored redirect destination
  const storedRedirect = sessionStorage.getItem(REDIRECT_KEYS[provider.value])
  sessionStorage.removeItem(REDIRECT_KEYS[provider.value])
  const finalRedirect = getSafeRedirectUrl(storedRedirect) ?? "/home"

  setTimeout(() => {
    navigateTo(finalRedirect)
  }, 2000)
}

onMounted(handleCallback)

useHead({ title: "Signing you in..." })
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center gap-6 bg-brand-gray-light p-4 dark:bg-background">
    <!-- Processing state -->
    <UCard
      v-if="status === 'processing'"
      class="w-full max-w-md border-border/60 bg-card/80 shadow-xl shadow-primary/15 backdrop-blur-xl"
    >
      <div class="flex flex-col items-center gap-4 p-8 text-center">
        <UIcon
          name="i-lucide-loader-circle"
          class="h-10 w-10 animate-spin text-primary"
        />
        <div>
          <h1 class="text-xl font-semibold">Completing sign in...</h1>
          <p class="mt-1 text-sm text-muted-foreground">Please wait while we finish setting up your account.</p>
        </div>
      </div>
    </UCard>

    <!-- Error state -->
    <UCard
      v-else-if="status === 'error'"
      class="w-full max-w-md border-border/60 bg-card/80 shadow-xl shadow-primary/15 backdrop-blur-xl"
    >
      <div class="flex flex-col items-center gap-4 p-8 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-error/10">
          <UIcon
            name="i-lucide-circle-alert"
            class="h-6 w-6 text-error"
          />
        </div>
        <div>
          <h1 class="text-xl font-semibold">Authentication failed</h1>
          <UAlert
            class="mt-3"
            color="error"
            variant="subtle"
            icon="i-lucide-circle-alert"
          >
            <UAlertDescription>{{ errorMessage }}</UAlertDescription>
          </UAlert>
        </div>
        <UButton
          variant="ghost"
          color="neutral"
          to="/login"
        >
          Back to Login
        </UButton>
      </div>
    </UCard>

    <!-- Success state -->
    <UCard
      v-else
      class="w-full max-w-md border-border/60 bg-card/80 shadow-xl shadow-primary/15 backdrop-blur-xl"
    >
      <div class="flex flex-col items-center gap-4 p-8 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-success/10">
          <UIcon
            name="i-lucide-circle-check"
            class="h-6 w-6 text-success"
          />
        </div>
        <div>
          <h1 class="text-xl font-semibold">Signed in successfully!</h1>
          <p class="mt-1 text-sm text-muted-foreground">Redirecting you...</p>
        </div>
        <div class="h-1 w-full max-w-xs overflow-hidden rounded-full bg-primary/20">
          <div class="h-full w-1/2 animate-pulse rounded-full bg-primary" />
        </div>
      </div>
    </UCard>
  </div>
</template>