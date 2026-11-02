<script setup lang="ts">
/**
 * FormField — Nuxt port of shadcn's FormField: binds a vee-validate field and
 * exposes `componentField` + `errorMessage` to the scoped slot.
 */
import { useField } from "vee-validate"

const props = defineProps<{
  name: string
}>()

const { value, errorMessage } = useField<string>(() => props.name)

const componentField = computed(() => ({
  modelValue: value.value,
  "onUpdate:modelValue": (val: unknown) => {
    value.value = val as never
  },
}))
</script>

<template>
  <slot
    :component-field="componentField"
    :error-message="errorMessage"
  />
</template>