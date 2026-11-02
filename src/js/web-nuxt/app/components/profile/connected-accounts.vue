<script setup lang="ts">
/**
 * ConnectedAccounts — Nuxt port of `components/profile/connected-accounts.tsx`.
 * Lists linked OAuth accounts with link / unlink actions.
 */
import { oAuthConfig, profileOAuthAccounts, profileOAuthLink, profileOAuthUnlink } from "#shared/api/sdk.gen"
import type { OAuthAccountInfo } from "#shared/api/types.gen"
import { apiErrorMessage } from "~/composables/api"

const toast = useToast()

const {
  data: accountsData,
  status: accountsStatus,
  refresh,
} = await useAsyncData<{ items: OAuthAccountInfo[] }>("oauth-accounts", async () => {
  const response = await profileOAuthAccounts()
  return { items: response.data?.items ?? [] }
})
const accounts = computed(() => accountsData.value?.items ?? [])
const isLoading = computed(() => accountsStatus.value === "pending")
const isError = computed(() => accountsStatus.value === "error")

const { data: oauthConfig } = await useAsyncData<{ githubEnabled?: boolean; googleEnabled?: boolean }>("oauth-config", async () => {
  const response = await oAuthConfig()
  return { githubEnabled: response.data?.githubEnabled, googleEnabled: response.data?.googleEnabled }
})

const linkedProviders = computed(() => new Set(accounts.value.map((account) => account.provider)))

const linkPending = ref(false)

const handleLink = async (provider: "google" | "github") => {
  try {
    const redirectUrl = `${window.location.origin}/profile`
    const response = await profileOAuthLink({ path: { provider }, query: { redirect_url: redirectUrl } })
    if (response.data?.authorizationUrl) {
      window.location.href = response.data.authorizationUrl
      return
    }
    toast.add({ title: "Unable to start OAuth flow", color: "error", icon: "i-lucide-circle-alert" })
  } catch (error) {
    toast.add({ title: "Unable to start OAuth flow", description: apiErrorMessage(error) || "Try again later", color: "error", icon: "i-lucide-circle-alert" })
  }
}

const handleUnlink = async (provider: string) => {
  try {
    await profileOAuthUnlink({ path: { provider } })
    toast.add({ title: `Unlinked ${provider}`, color: "success", icon: "i-lucide-circle-check" })
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to unlink account", description: apiErrorMessage(error) || "Try again later", color: "error", icon: "i-lucide-circle-alert" })
  }
}

const providerIcon = (provider: string) => (provider === "google" ? "i-simple-icons-google" : "i-simple-icons-github")
</script>

<template>
  <div v-if="isLoading">
    <USkeleton class="h-48 w-full rounded-lg" />
  </div>

  <UCard v-else-if="isError">
    <template #header>
      <div class="space-y-1">
        <h2 class="font-semibold">Connected accounts</h2>
        <p class="text-sm text-muted-foreground">We could not load your connected accounts.</p>
      </div>
    </template>
  </UCard>

  <UCard v-else>
    <template #header>
      <div class="space-y-1">
        <h2 class="font-semibold">Connected accounts</h2>
        <p class="text-sm text-muted-foreground">Manage your linked OAuth providers.</p>
      </div>
    </template>

    <div class="space-y-4">
      <p
        v-if="accounts.length === 0"
        class="text-sm text-muted-foreground"
      >
        No connected accounts yet.
      </p>
      <div class="space-y-3">
        <div
          v-for="account in accounts"
          :key="account.provider"
          class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/60 bg-muted/30 px-4 py-3"
        >
          <div class="flex items-center gap-3">
            <UIcon
              :name="providerIcon(account.provider)"
              class="h-4 w-4"
            />
            <div>
              <p class="font-medium capitalize">{{ account.provider }}</p>
              <p class="text-sm text-muted-foreground">{{ account.email }}</p>
            </div>
          </div>
          <UButton
            variant="outline"
            color="neutral"
            size="sm"
            @click="handleUnlink(account.provider)"
          >
            Unlink
          </UButton>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <ProfileOauthLinkButton
          v-if="oauthConfig?.googleEnabled && !linkedProviders.has('google')"
          provider="google"
          :disabled="linkPending"
          @click="handleLink('google')"
        />
        <ProfileOauthLinkButton
          v-if="oauthConfig?.githubEnabled && !linkedProviders.has('github')"
          provider="github"
          :disabled="linkPending"
          @click="handleLink('github')"
        />
      </div>
    </div>
  </UCard>
</template>