<script setup lang="ts">
/**
 * Google sign-in button — Nuxt port of the React app's
 * `components/auth/google-signin-button.tsx`.
 */
import { apiAuthOauthGoogleGoogleAuthorize } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

/** Key used to store the post-auth redirect destination in sessionStorage */
const GOOGLE_AUTH_REDIRECT_KEY = "google_auth_redirect"

const props = withDefaults(
  defineProps<{
    variant?: "signin" | "signup" | "link"
    redirectUrl?: string
    authRedirect?: string
  }>(),
  { variant: "signin" },
)

const toast = useToast()
const isPending = ref(false)

const handleClick = async () => {
  isPending.value = true
  try {
    const targetUrl = props.redirectUrl ?? `${window.location.origin}/auth/google/callback`
    const { data, error } = await apiAuthOauthGoogleGoogleAuthorize({
      query: { redirect_url: targetUrl },
    })
    if (error) {
      throw new Error("Failed to initiate OAuth")
    }
    if (data?.authorizationUrl) {
      // Store the post-auth redirect destination before leaving for OAuth
      if (props.authRedirect) {
        sessionStorage.setItem(GOOGLE_AUTH_REDIRECT_KEY, props.authRedirect)
      } else {
        sessionStorage.removeItem(GOOGLE_AUTH_REDIRECT_KEY)
      }
      window.location.href = data.authorizationUrl
    } else {
      toast.add({ title: "Failed to get authorization URL", color: "error" })
    }
  } catch (error) {
    toast.add({ title: (error as Error).message || "Failed to sign in with Google", color: "error" })
  } finally {
    isPending.value = false
  }
}

const buttonText = computed(() => {
  switch (props.variant) {
    case "signup":
      return "Sign up with Google"
    case "link":
      return "Link Google Account"
    default:
      return "Sign in with Google"
  }
})

void apiErrorMessage
</script>

<template>
  <UButton
    type="button"
    variant="outline"
    color="neutral"
    block
    :loading="isPending"
    @click="handleClick"
  >
    <template #leading>
      <svg
        class="h-4 w-4"
        viewBox="0 0 24 24"
      >
        <path
          fill="currentColor"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="currentColor"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="currentColor"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="currentColor"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
    </template>
    {{ buttonText }}
  </UButton>
</template>