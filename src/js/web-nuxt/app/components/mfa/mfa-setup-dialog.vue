<script setup lang="ts">
/**
 * MfaSetupDialog — Nuxt port of `components/mfa/mfa-setup-dialog.tsx`.
 * QR-code + secret + 6-digit confirm flow; shows backup codes on success.
 */
import { confirmMfaSetup, initiateMfaSetup, type MfaSetup } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

const props = withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })
void props

const toast = useToast()

const open = defineModel<boolean>("open", { default: false })
const setup = ref<MfaSetup | null>(null)
const codes = ref<string[] | null>(null)
const code = ref("")
const submitting = ref(false)

watchEffect(() => {
  if (!open.value) {
    setup.value = null
    codes.value = null
    code.value = ""
    return
  }
  if (setup.value || submitting.value) return
  initiateMfaSetup()
    .then((response) => {
      setup.value = response.data ?? null
    })
    .catch((error: unknown) => {
      toast.add({ title: "Unable to start MFA setup", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
    })
})

const isInitiating = computed(() => open.value && !setup.value && !codes.value)

const handleConfirm = async () => {
  if (!code.value || code.value.length < 6) {
    toast.add({ title: "Enter the 6-digit code from your authenticator app", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  submitting.value = true
  try {
    const response = await confirmMfaSetup({ body: { code: code.value } })
    codes.value = response.data?.codes ?? []
  } catch (error) {
    toast.add({ title: "Verification failed", description: apiErrorMessage(error) || "Check the code and try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    submitting.value = false
  }
}

const isLoading = computed(() => submitting.value)
</script>

<template>
  <UModal
    v-model:open="open"
    title="Enable multi-factor authentication"
    description="Scan the QR code with your authenticator app, then enter the 6-digit verification code."
  >
    <UButton :disabled="disabled">Enable MFA</UButton>

    <template #body>
      <BackupCodesDisplay
        v-if="codes"
        :codes="codes"
        description="Save these codes in a secure place. Each code can be used once if you lose access to your authenticator."
      />

      <div
        v-else-if="isInitiating"
        class="space-y-4"
      >
        <USkeleton class="h-44 w-full" />
        <USkeleton class="h-10 w-full" />
      </div>

      <div
        v-else-if="setup"
        class="space-y-4"
      >
        <div class="flex justify-center rounded-lg border border-border/60 bg-white p-4">
          <img
            :src="setup.qrCode"
            alt="MFA QR code"
            class="h-48 w-48"
          >
        </div>
        <div class="rounded-lg border border-border/60 bg-muted/30 px-4 py-3 font-mono text-sm break-all">{{ setup.secret }}</div>
        <MfaTotpInput
          v-model="code"
          :disabled="isLoading"
          auto-focus
        />
      </div>
    </template>

    <template #footer>
      <UButton
        v-if="codes"
        @click="open = false"
      >
        Done
      </UButton>
      <UButton
        v-else
        :disabled="isLoading || code.length < 6"
        :loading="isLoading"
        @click="handleConfirm"
      >
        Verify &amp; finish
      </UButton>
    </template>
  </UModal>
</template>