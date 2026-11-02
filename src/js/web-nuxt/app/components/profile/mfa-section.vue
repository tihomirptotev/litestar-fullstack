<script setup lang="ts">
/**
 * MfaSection — Nuxt port of `components/profile/mfa-section.tsx`.
 * Multi-factor auth card: setup / disable / regenerate backup codes.
 */
import { disableMfa, getMfaStatus, initiateDisableMfaOAuth, regenerateMfaBackupCodes } from "#shared/api/sdk.gen"
import type { MfaStatus } from "#shared/api/types.gen"
import { apiErrorMessage } from "~/composables/api"

const auth = useAuth()
const toast = useToast()

const {
  data: mfaStatus,
  status: queryStatus,
  refresh,
} = await useAsyncData<MfaStatus | null>("mfa-status", async () => {
  const response = await getMfaStatus()
  return response.data ?? null
})
const isLoading = computed(() => queryStatus.value === "pending")
const isError = computed(() => queryStatus.value === "error")

// Regenerate backup codes dialog
const regenOpen = ref(false)
const regenPassword = ref("")
const regenCodes = ref<string[] | null>(null)
const regenPending = ref(false)

const handleRegenerate = async () => {
  if (!regenPassword.value) {
    toast.add({ title: "Enter your password to regenerate backup codes", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  regenPending.value = true
  try {
    const response = await regenerateMfaBackupCodes({ body: { password: regenPassword.value } })
    regenCodes.value = response.data?.codes ?? []
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to regenerate codes", description: apiErrorMessage(error) || "Try again later", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    regenPending.value = false
  }
}

const regenDialogOpen = computed({
  get: () => regenOpen.value,
  set: (value: boolean) => {
    regenOpen.value = value
    if (!value) {
      regenPassword.value = ""
      regenCodes.value = null
    }
  },
})

// Disable MFA (password or OAuth re-auth)
const disableOpen = ref(false)
const disablePassword = ref("")
const disablePending = ref(false)

const hasPassword = computed(() => auth.user.value?.hasPassword ?? true)
const oauthProvider = computed(() => auth.user.value?.oauthAccounts?.[0]?.oauthName)

const handleDisable = async () => {
  if (!disablePassword.value) {
    toast.add({ title: "Enter your password to disable MFA", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  disablePending.value = true
  try {
    await disableMfa({ body: { password: disablePassword.value } })
    disableDialogOpen.value = false
    disablePassword.value = ""
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to disable MFA", description: apiErrorMessage(error) || "Check your password and try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    disablePending.value = false
  }
}

const handleOAuthDisable = async () => {
  if (!oauthProvider.value) {
    toast.add({ title: "No linked OAuth account found", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  disablePending.value = true
  try {
    const response = await initiateDisableMfaOAuth({ path: { provider: oauthProvider.value } })
    if (response.data?.authorizationUrl) {
      window.location.href = response.data.authorizationUrl
    }
  } catch (error) {
    toast.add({ title: "Unable to start OAuth verification", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    disablePending.value = false
  }
}

const disableDialogOpen = computed({
  get: () => disableOpen.value,
  set: (value: boolean) => {
    disableOpen.value = value
    if (!value) disablePassword.value = ""
  },
})

const formatProviderName = (provider: string) => provider.charAt(0).toUpperCase() + provider.slice(1)
</script>

<template>
  <div v-if="isLoading">
    <USkeleton class="h-48 w-full rounded-lg" />
  </div>

  <UCard v-else-if="isError || !mfaStatus">
    <template #header>
      <div class="space-y-1">
        <h2 class="font-semibold">Multi-factor authentication</h2>
        <p class="text-sm text-muted-foreground">We could not load MFA status.</p>
      </div>
    </template>
  </UCard>

  <UCard v-else>
    <template #header>
      <div class="space-y-1">
        <h2 class="font-semibold">Multi-factor authentication</h2>
        <p class="text-sm text-muted-foreground">
          {{ mfaStatus.enabled ? "MFA is enabled on your account." : "Add an extra layer of security to your account." }}
        </p>
      </div>
    </template>

    <div class="space-y-4">
      <template v-if="mfaStatus.enabled">
        <div class="flex flex-wrap gap-2">
          <UButton
            variant="outline"
            color="neutral"
            @click="disableDialogOpen = true"
          >
            Disable MFA
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            @click="regenDialogOpen = true"
          >
            Regenerate backup codes
          </UButton>
        </div>
        <p
          v-if="mfaStatus.backupCodesRemaining !== null"
          class="text-sm text-muted-foreground"
        >
          Backup codes remaining: {{ mfaStatus.backupCodesRemaining ?? 0 }}
        </p>
      </template>
      <MfaSetupDialog v-else />
    </div>

    <!-- Regenerate backup codes dialog -->
    <UModal
      v-model:open="regenDialogOpen"
      title="Regenerate backup codes"
      description="Confirm your password to generate a fresh set of codes."
    >
      <template #body>
        <BackupCodesDisplay
          v-if="regenCodes"
          :codes="regenCodes"
          description="These codes replace your previous set. Store them securely."
        />
        <UInput
          v-else
          v-model="regenPassword"
          type="password"
          placeholder="Password"
        />
      </template>
      <template #footer>
        <UButton
          v-if="regenCodes"
          @click="regenDialogOpen = false"
        >
          Done
        </UButton>
        <UButton
          v-else
          :loading="regenPending"
          @click="handleRegenerate"
        >
          Regenerate
        </UButton>
      </template>
    </UModal>

    <!-- Disable MFA dialog -->
    <UModal
      v-model:open="disableDialogOpen"
      title="Disable multi-factor authentication"
      :description="hasPassword ? 'Confirm your password to turn off MFA.' : 'Re-authenticate with your linked account to turn off MFA.'"
    >
      <template #body>
        <template v-if="hasPassword">
          <div class="space-y-4">
            <UInput
              v-model="disablePassword"
              type="password"
              placeholder="Password"
            />
            <div class="flex justify-end gap-2">
              <UButton
                :loading="disablePending"
                @click="handleDisable"
              >
                Disable MFA
              </UButton>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="flex justify-end gap-2">
            <UButton
              :loading="disablePending"
              @click="handleOAuthDisable"
            >
              Verify with {{ oauthProvider ? formatProviderName(oauthProvider) : "OAuth" }}
            </UButton>
          </div>
        </template>
      </template>
    </UModal>
  </UCard>
</template>