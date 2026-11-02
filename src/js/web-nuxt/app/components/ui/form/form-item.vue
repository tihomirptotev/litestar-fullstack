<script setup lang="ts">
/**
 * FormItem — Nuxt port of shadcn's FormItem: labeled field wrapper.
 */
defineProps<{ class?: string }>()
</script>

<template>
  <div
    class="grid gap-2"
    :class="class"
  >
    <slot />
  </div>
</template>