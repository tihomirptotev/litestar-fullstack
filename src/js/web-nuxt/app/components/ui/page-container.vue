<script setup lang="ts">
/**
 * PageContainer — Nuxt port of `components/ui/page-layout.tsx` PageContainer.
 */
const props = withDefaults(
  defineProps<{
    maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "4xl" | "full"
  }>(),
  { maxWidth: "2xl" },
)

const maxWidthClasses: Record<string, string> = {
  sm: "max-w-screen-sm",
  md: "max-w-screen-md",
  lg: "max-w-screen-lg",
  xl: "max-w-screen-xl",
  "2xl": "max-w-screen-2xl",
  "4xl": "max-w-[1400px]",
  full: "max-w-full",
}
</script>

<template>
  <div
    class="w-full px-4 py-8 md:px-6 md:py-10"
    :class="[maxWidthClasses[props.maxWidth]]"
  >
    <slot />
  </div>
</template>