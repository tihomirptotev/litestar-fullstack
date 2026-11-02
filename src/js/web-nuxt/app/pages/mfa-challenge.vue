<script setup lang="ts">
/**
 * MFA challenge page — Nuxt port of the React app's
 * `routes/_public/mfa-challenge.tsx`.
 */
import { verifyMfaChallenge } from "#shared/api/sdk.gen"
import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import { apiErrorMessage, unwrapAs } from "~/composables/api"
import { useAuth } from "~/composables/useAuth"
import { getSafeRedirectUrl } from "~/utils/redirect-utils"

definePageMeta({ layout: false })

useHead({ title: "Two-factor authentication — Litestar Fullstack" })

const route = useRoute()
const toast = useToasterCompat()

// Local sonner-like toaster (mirrors useAuth's internal helper).
function useToasterCompat() {
  const { add } = useToast()
  return {
    error: (message: string, opts?: { description?: string }) => add({ title: message, description: opts?.description, color: "error", icon: "i-lucide-circle-alert" }),
    success: (message: string, opts?: { description?: string }) => add({ title: message, description: opts?.description, color: "success", icon: "i-lucide-circle-check" }),
  }
}

const auth = useAuth()

const redirectParam = computed(() => (route.query.redirect as string | undefined) || null)
const finalRedirect = getSafeRedirectUrl(redirectParam.value)

const tab = ref<"totp" | "recovery">("totp")
const code = ref("")
const recoveryCode = ref("")
const isPending = ref(false)

const handleVerify = async () => {
  isPending.value = true
  try {
    const payload = tab.value === "totp" ? { code: code.value } : { recovery_code: recoveryCode.value.trim().toUpperCase() }
    const response = await unwrapAs<unknown, unknown, { access_token?: string }>(
      // MFA challenge authenticates via the mfa_challenge cookie — no bearer header.
      verifyMfaChallenge({
        body: payload,
        security: [],
      } as never),
    )
    const accessToken = response?.access_token
    if (!accessToken) {
      toast.error("Verification failed")
      return
    }
    await auth.completeMfaLogin(accessToken)
    toast.success("MFA verified")
    await navigateTo(finalRedirect)
  } catch (error) {
    toast.error("Verification failed", {
      description: error instanceof Error ? error.message : apiErrorMessage(error) || "Try again",
    })
  } finally {
    isPending.value = false
  }
}

const disableAction = computed(() => isPending.value || (tab.value === "totp" ? code.value.length < 6 : !recoveryCode.value))
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <AuthHeroPanel
      :show-testimonial="false"
      description="Two-factor authentication keeps your account secure."
    />

    <div class="flex flex-1 flex-col items-center justify-center bg-brand-gray-light px-4 py-12 dark:bg-background">
      <div class="w-full max-w-md space-y-6">
        <div class="text-center">
          <h1 class="text-2xl font-semibold tracking-tight">
            Verify your identity
          </h1>
          <p class="mt-2 text-sm text-muted-foreground">Enter a code from your authenticator app or a backup code.</p>
        </div>

        <UTabs
          v-model="tab"
          :items="[
            { label: 'Authenticator', value: 'totp' },
            { label: 'Backup code', value: 'recovery' },
          ]"
          :ui="{ list: 'grid w-full grid-cols-2', content: 'space-y-3 pt-4' }"
        >
          <template #totp>
            <MfaTotpInput
              v-model="code"
              :disabled="isPending"
              auto-focus
            />
          </template>
          <template #recovery>
            <UInput
              v-model="recoveryCode"
              placeholder="XXXX-XXXX"
              :disabled="isPending"
            />
          </template>
        </UTabs>

        <UButton
          block
          :disabled="disableAction"
          :loading="isPending"
          @click="handleVerify"
        >
          Verify
        </UButton>
      </div>
    </div>
  </div>
</template>