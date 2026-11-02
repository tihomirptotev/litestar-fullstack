<script setup lang="ts">
/**
 * OAuthLinkButton — Nuxt port of `components/profile/oauth-link-button.tsx`.
 * Outlined button that starts an OAuth account-link flow.
 */
const props = defineProps<{
  provider: "google" | "github"
  disabled?: boolean
}>()

const emit = defineEmits<{ click: [] }>()

const providerLabels: Record<"google" | "github", string> = {
  google: "Google",
  github: "GitHub",
}
const providerIcons: Record<"google" | "github", string> = {
  google: "i-simple-icons-google",
  github: "i-simple-icons-github",
}
void props
</script>

<template>
  <UButton
    variant="outline"
    color="neutral"
    class="justify-start gap-2"
    :disabled="disabled"
    :icon="providerIcons[provider]"
    @click="emit('click')"
  >
    Link {{ providerLabels[provider] }}
  </UButton>
</template>