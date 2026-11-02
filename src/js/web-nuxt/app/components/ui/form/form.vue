<script setup lang="ts">
/**
 * Form primitives — Nuxt port of the React app's shadcn `Form` components:
 * minimal passthroughs coordinating vee-validate + Nuxt UI.
 */
import { FieldContextKey } from "vee-validate"
import type { InjectionKey, Ref } from "vue"

defineOptions({ inheritAttrs: false })
</script>

<template>
  <slot />
</template>