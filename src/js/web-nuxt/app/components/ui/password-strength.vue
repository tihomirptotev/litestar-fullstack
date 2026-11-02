<script setup lang="ts">
/**
 * PasswordStrength — Nuxt port of the React app's `components/ui/password-strength.tsx`.
 * Meter + requirements checklist; the React framer-motion spring is replaced by
 * a transition on the progress width.
 */
import { getPasswordStrength } from "~/utils/password-strength"

const props = defineProps<{
  password: string
}>()

const info = computed(() => getPasswordStrength(props.password))

const meterColor = computed(() => {
  switch (info.value.strength) {
    case "strong":
      return "bg-success"
    case "medium":
      return "bg-warning"
    default:
      return "bg-error"
  }
})

const requirementRows = computed(() => [
  { key: "length", label: "At least 12 characters", ok: info.value.requirements.length },
  { key: "uppercase", label: "Uppercase letter", ok: info.value.requirements.uppercase },
  { key: "lowercase", label: "Lowercase letter", ok: info.value.requirements.lowercase },
  { key: "digits", label: "Number", ok: info.value.requirements.digits },
  { key: "special", label: "Special character", ok: info.value.requirements.special },
  { key: "notCommon", label: "Not a common password", ok: info.value.requirements.notCommon },
])
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="meterColor"
          :style="{ width: `${Math.min(100, (info.score / 10) * 100)}%` }"
        />
      </div>
      <span class="text-xs text-muted-foreground capitalize">{{ info.strength }}</span>
    </div>

    <ul class="grid grid-cols-1 gap-1 sm:grid-cols-2">
      <li
        v-for="row in requirementRows"
        :key="row.key"
        class="flex items-center gap-1.5 text-xs"
        :class="row.ok ? 'text-success' : 'text-muted-foreground'"
      >
        <UIcon
          :name="row.ok ? 'i-lucide-circle-check' : 'i-lucide-circle'"
          class="h-3.5 w-3.5"
        />
        {{ row.label }}
      </li>
    </ul>

    <ul
      v-if="info.feedback.length"
      class="space-y-1"
    >
      <li
        v-for="tip in info.feedback"
        :key="tip"
        class="flex items-center gap-1.5 text-xs text-warning"
      >
        <UIcon
          name="i-lucide-circle-x"
          class="h-3.5 w-3.5"
        />
        {{ tip }}
      </li>
    </ul>
  </div>
</template>