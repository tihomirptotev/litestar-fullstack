<script setup lang="ts">
/**
 * Button — port of `src/components/Button.tsx` (react-email) to Maizzle.
 * Styled CTA button; renders an `<a>` styled as a button.
 */
import { emailTheme } from "../lib/theme"

const props = withDefaults(
  defineProps<{
    href: string
    variant?: "primary" | "success" | "secondary"
  }>(),
  {
    variant: "primary",
  },
)

const colors = {
  primary: {
    background: emailTheme.colors.brandGold,
    color: emailTheme.colors.brandNavy,
  },
  success: {
    background: emailTheme.colors.successBg,
    color: "#ffffff",
  },
  secondary: {
    background: emailTheme.colors.secondaryBg,
    color: "#ffffff",
  },
}

const variantColors = colors[props.variant]

const button = {
  display: "inline-block",
  padding: "12px 32px",
  backgroundColor: variantColors.background,
  color: variantColors.color,
  textDecoration: "none",
  borderRadius: emailTheme.radius.button,
  fontWeight: 600,
  fontSize: "14px",
  lineHeight: "20px",
  textAlign: "center",
}
</script>

<template>
  <a
    :href="href"
    :style="button"
    target="_blank"
  >
    <slot />
  </a>
</template>