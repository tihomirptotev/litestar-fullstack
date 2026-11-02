<script setup lang="ts">
/**
 * TotpInput — Nuxt port of `components/mfa/totp-input.tsx`.
 * 6-digit numeric input for TOTP verification codes.
 */
const code = defineModel<string>({ required: true })

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    autoFocus?: boolean
  }>(),
  { disabled: false, autoFocus: false },
)

const input = useTemplateRef<HTMLInputElement>("input")

onMounted(() => {
  if (props.autoFocus) input.value?.focus()
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const digits = target.value.replace(/\D/g, "").slice(0, 6)
  code.value = digits
  target.value = digits
}
</script>

<template>
  <UInput
    ref="input"
    v-model="code"
    type="text"
    inputmode="numeric"
    autocomplete="one-time-code"
    placeholder="123456"
    :disabled="disabled"
    class="text-center font-mono text-lg tracking-[0.5em]"
    @input="handleInput"
  />
</template>