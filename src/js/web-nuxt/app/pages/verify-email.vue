<script setup lang="ts">
/**
 * Verify email page — Nuxt port of the React app's
 * `routes/_public/verify-email.tsx` (VerifyEmailPage; the exported
 * ResendVerificationPage was unused in the React app's route tree).
 */
import { apiEmailVerificationRequestRequestVerification, apiEmailVerificationVerifyVerifyEmail } from "#shared/api/sdk.gen"
import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import { apiErrorMessage } from "~/composables/api"
import { useAuth } from "~/composables/useAuth"

definePageMeta({ layout: false })

useHead({ title: "Verify email — Litestar Fullstack" })

const route = useRoute()
const toast = useToast()
const auth = useAuth()

type Status = "verifying" | "success" | "error"
const status = ref<Status>("verifying")
const errorMessage = ref("")

const token = computed(() => (route.query.token as string | undefined) || "")

const verifyEmail = async (verificationToken: string) => {
  status.value = "verifying"
  try {
    await apiEmailVerificationVerifyVerifyEmail({ body: { token: verificationToken } })
    status.value = "success"
    toast.add({ title: "Email verified successfully!", color: "success" })
    await auth.checkAuth()
    setTimeout(() => {
      navigateTo("/home")
    }, 3000)
  } catch (error: unknown) {
    status.value = "error"
    errorMessage.value = apiErrorMessage(error) || "Verification failed"
    toast.add({ title: errorMessage.value, color: "error" })
  }
}

onMounted(() => {
  if (token.value) {
    verifyEmail(token.value)
  } else {
    status.value = "error"
    errorMessage.value = "Verification token is missing"
  }
})
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <AuthHeroPanel
      :show-testimonial="false"
      description="Verify your email to access all features."
    />

    <div class="flex flex-1 flex-col items-center justify-center bg-brand-gray-light px-4 py-12 dark:bg-background">
      <div class="w-full max-w-md space-y-6">
        <div class="text-center">
          <h1 class="text-2xl font-semibold tracking-tight">
            {{ status === "verifying" && "Verifying your email..." }}
            {{ status === "success" && "Email Verified!" }}
            {{ status === "error" && "Verification Failed" }}
          </h1>
        </div>

        <!-- Verifying -->
        <div
          v-if="status === 'verifying'"
          class="flex flex-col items-center space-y-4"
        >
          <UIcon
            name="i-lucide-loader-circle"
            class="h-8 w-8 animate-spin text-primary"
          />
          <p class="text-sm text-muted-foreground">Please wait while we verify your email address...</p>
        </div>

        <!-- Success -->
        <div
          v-else-if="status === 'success'"
          class="flex flex-col items-center space-y-4"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
            <UIcon
              name="i-lucide-circle-check"
              class="h-6 w-6 text-green-600 dark:text-green-400"
            />
          </div>
          <div class="text-center">
            <p class="mb-2 font-medium">Your email has been verified successfully!</p>
            <p class="text-sm text-muted-foreground">You will be redirected to the home page shortly...</p>
          </div>
          <UButton
            block
            to="/home"
          >
            Go to Home
          </UButton>
        </div>

        <!-- Error -->
        <div
          v-else
          class="flex flex-col items-center space-y-4"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
            <UIcon
              name="i-lucide-circle-x"
              class="h-6 w-6 text-red-600 dark:text-red-400"
            />
          </div>
          <UAlert
            variant="subtle"
            color="error"
            :title="errorMessage"
          />
          <div class="flex w-full flex-col space-y-2">
            <template v-if="errorMessage.includes('expired')">
              <p class="mb-2 text-center text-sm text-muted-foreground">Your verification link has expired. Please request a new one.</p>
              <UButton
                block
                to="/login"
              >
                Go to Login
              </UButton>
            </template>
            <template v-else>
              <UButton
                block
                to="/login"
              >
                Back to Login
              </UButton>
              <UButton
                v-if="token"
                variant="outline"
                color="neutral"
                block
                :disabled="status === 'verifying'"
                @click="verifyEmail(token)"
              >
                Try Again
              </UButton>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>