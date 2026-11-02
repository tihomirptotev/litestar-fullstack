<script setup lang="ts">
/**
 * EmailLayout — port of `src/components/Layout.tsx` (react-email) to Maizzle.
 *
 * Wraps the full email document: Html/Head/Preheader/Body + brand chrome
 * (Header/Footer). Slot content renders inside the content section.
 */
import { emailTheme } from "../lib/theme"
import EmailFooter from "./Footer.vue"
import EmailHeader from "./Header.vue"

defineProps<{
  /** Preview / preheader text (hidden inbox snippet) */
  preview: string
  /** Application name shown in header + footer */
  appName: string
}>()

const main = {
  backgroundColor: emailTheme.colors.bodyBg,
  fontFamily: emailTheme.fonts.primary,
  lineHeight: emailTheme.lineHeight,
  color: emailTheme.colors.textPrimary,
  padding: emailTheme.spacing.bodyPadding,
}

const container = {
  maxWidth: "600px",
  margin: "0 auto",
  backgroundColor: emailTheme.colors.containerBg,
  borderRadius: emailTheme.radius.container,
  overflow: "hidden",
  border: `1px solid ${emailTheme.colors.border}`,
  boxShadow: emailTheme.shadows.container,
}

const content = {
  padding: emailTheme.spacing.containerPadding,
}
</script>

<template>
  <Html lang="en">
    <Head />
    <Preheader>{{ preview }}</Preheader>
    <!-- Body.vue hardcodes its own style and drops `style` bindings, so the
         page-level look (dark background, padding, font) is applied to a
         full-width Section inside the Body. -->
    <Body bgcolor="#0f1322">
      <Section :style="main">
        <Container :style="container">
          <EmailHeader :app-name="appName" />
          <Section :style="content">
            <slot />
          </Section>
          <EmailFooter :app-name="appName" />
        </Container>
      </Section>
    </Body>
  </Html>
</template>