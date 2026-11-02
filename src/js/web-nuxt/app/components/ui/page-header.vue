<script setup lang="ts">
/**
 * PageHeader — Nuxt port of `components/ui/page-layout.tsx` PageHeader
 * (framer-motion fade-up replaced with a transition).
 */
defineProps<{
  eyebrow?: string
  title: string
  description?: string
}>()
</script>

<template>
  <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
    <div class="space-y-2">
      <p
        v-if="eyebrow"
        class="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground"
      >
        {{ eyebrow }}
      </p>
      <h1 class="text-3xl font-semibold tracking-tight md:text-4xl">
        {{ title }}
      </h1>
      <p
        v-if="description"
        class="max-w-2xl text-muted-foreground"
      >
        {{ description }}
      </p>
    </div>
    <div
      v-if="$slots.actions"
      class="flex flex-wrap gap-3"
    >
      <slot name="actions" />
    </div>
  </div>
</template>