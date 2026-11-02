<script setup lang="ts">
/**
 * FormDescription — Nuxt port of the React app's `ui/form.tsx` FormDescription.
 */
defineProps<{
  class?: string
}>()
</script>

<template>
  <p
    class="text-sm text-muted-foreground"
    :class="class"
  >
    <slot />
  </p>
</template>