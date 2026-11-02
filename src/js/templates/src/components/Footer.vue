<script setup lang="ts">
/**
 * Footer — port of `src/components/Footer.tsx` (react-email) to Maizzle.
 */
import { emailTheme } from "../lib/theme"

defineProps<{
  appName: string
}>()

const year = new Date().getFullYear()

const footer = {
  backgroundColor: emailTheme.colors.footerBg,
  padding: emailTheme.spacing.footerPadding,
  textAlign: "center",
  borderTop: `1px solid ${emailTheme.colors.border}`,
}
</script>

<template>
  <div :style="footer">
    <Text
      :style="{
        margin: '0 0 8px 0',
        color: emailTheme.colors.textMuted,
        fontSize: '12px',
      }"
    >
      {{ appName }}
    </Text>
    <Text
      :style="{
        margin: 0,
        color: emailTheme.colors.textFooter,
        fontSize: '11px',
      }"
    >
      &copy; {{ year }} All rights reserved.
    </Text>
    <Text
      :style="{
        margin: '8px 0 0 0',
        color: emailTheme.colors.textFooter,
        fontSize: '11px',
      }"
    >
      You received this email because you have an account with {{ appName }}.
    </Text>
  </div>
</template>