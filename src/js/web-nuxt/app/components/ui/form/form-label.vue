<script setup lang="ts">
/**
 * FormLabel — Nuxt port of shadcn's FormLabel.
 */
defineProps<{ class?: string }>()
</script>

<template>
  <label
    class="text-sm font-medium leading-none"
    :class="class"
  >
    <slot />
  </label>
</template>