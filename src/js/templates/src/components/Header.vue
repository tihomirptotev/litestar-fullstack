<script setup lang="ts">
/**
 * Header — port of `src/components/Header.tsx` (react-email) to Maizzle.
 * Gold banner with the app name.
 */
import { emailTheme } from "../lib/theme"

defineProps<{
  appName: string
}>()

const banner = {
  backgroundColor: emailTheme.colors.brandGold,
  padding: emailTheme.spacing.headerPadding,
  textAlign: "center",
}
</script>

<template>
  <div :style="banner">
    <Heading
      :style="{
        margin: 0,
        color: emailTheme.colors.brandNavy,
        fontSize: '24px',
        fontWeight: 700,
        letterSpacing: '-0.5px',
      }"
    >
      {{ appName }}
    </Heading>
    <Text
      :style="{
        margin: '4px 0 0 0',
        color: `${emailTheme.colors.brandNavy}cc`,
        fontSize: '12px',
        fontWeight: 500,
      }"
    >
      Secure Application Platform
    </Text>
  </div>
</template>