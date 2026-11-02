<script setup lang="ts">
/**
 * Profile settings page — Nuxt port of the React app's
 * `routes/_app/profile/index.tsx`.
 * OAuth link success/error is reported via query params (redirect back from
 * the backend), cleaned up with a replace-navigation after toasting.
 */
definePageMeta({ layout: "app" })

const route = useRoute()
const toast = useToast()

// Handle OAuth link callback params
const linked = computed(() => route.query.linked as string | undefined)
const provider = computed(() => route.query.provider as string | undefined)
const oauthFailed = computed(() => route.query.oauth_failed as string | undefined)
const message = computed(() => route.query.message as string | undefined)

watchEffect(() => {
  // Handle successful OAuth link
  if (linked.value === "true" && provider.value) {
    const providerName = provider.value.charAt(0).toUpperCase() + provider.value.slice(1)
    toast.add({ title: `Successfully linked ${providerName} account`, color: "success", icon: "i-lucide-circle-check" })
    navigateTo({ path: "/profile", replace: true })
    return
  }
  // Handle OAuth error
  if (oauthFailed.value) {
    toast.add({ title: message.value || "Failed to link account", color: "error", icon: "i-lucide-circle-alert" })
    navigateTo({ path: "/profile", replace: true })
  }
})

useHead({ title: "Profile — Litestar Fullstack" })
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <PageHeader
        eyebrow="Account"
        title="Profile settings"
        description="Manage security, connected accounts, and authentication options."
      />

      <div class="grid gap-6 lg:grid-cols-2">
        <ProfileMfaSection />
        <ProfileConnectedAccounts />
      </div>
    </PageContainer>
  </div>
</template>