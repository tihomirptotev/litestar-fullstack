<script setup lang="ts">
/**
 * BackupCodesDisplay — Nuxt port of `components/mfa/backup-codes-display.tsx`.
 * Shows one-time backup codes in a grid with copy-to-clipboard.
 */
const props = withDefaults(
  defineProps<{
    codes: string[]
    title?: string
    description?: string
  }>(),
  { title: "Backup codes", description: undefined },
)

const toast = useToast()

const formatted = computed(() => props.codes.filter(Boolean))

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(formatted.value.join("\n"))
    toast.add({ title: "Backup codes copied", color: "success", icon: "i-lucide-clipboard-check" })
  } catch {
    toast.add({ title: "Unable to copy backup codes", color: "error", icon: "i-lucide-circle-alert" })
  }
}
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-semibold">{{ title }}</h2>
          <p
            v-if="description"
            class="text-sm text-muted-foreground"
          >
            {{ description }}
          </p>
        </div>
        <UButton
          variant="outline"
          color="neutral"
          size="sm"
          icon="i-lucide-copy"
          @click="handleCopy"
        >
          Copy
        </UButton>
      </div>
    </template>
    <div class="grid gap-2 sm:grid-cols-2">
      <div
        v-for="code in formatted"
        :key="code"
        class="rounded-md border border-border/60 bg-muted/40 px-3 py-2 font-mono text-sm text-foreground"
      >
        {{ code }}
      </div>
    </div>
  </UCard>
</template>