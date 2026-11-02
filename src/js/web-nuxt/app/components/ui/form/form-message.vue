<script setup lang="ts">
/**
 * FormMessage — Nuxt port of shadcn's FormMessage: renders the vee-validate
 * field error for the current FormField (or an explicit message).
 */
defineProps<{
  errorMessage?: string
  class?: string
}>()
</script>

<template>
  <p
    v-if="errorMessage"
    class="text-sm text-error"
    :class="class"
  >
    {{ errorMessage }}
  </p>
</template>