<script setup lang="ts">
/**
 * Email Verification Template — port of `src/emails/email-verification.tsx` to Maizzle.
 *
 * Placeholders (substituted by Python `str.replace`, keep literal!):
 * - {{APP_NAME}} - Application name
 * - {{USER_NAME}} - User's display name
 * - {{VERIFICATION_URL}} - Email verification link
 * - {{EXPIRES_HOURS}} - Token expiration time in hours
 */
import EmailButton from "../components/Button.vue"
import EmailLayout from "../components/EmailLayout.vue"

const linkBox = {
  margin: "0 0 24px 0",
  padding: "12px 16px",
  backgroundColor: "#1c2237",
  borderRadius: "6px",
  fontSize: "12px",
  color: "#FFB000",
  wordBreak: "break-all",
}
</script>

<template>
  <EmailLayout
    preview="Verify your email address"
    app-name="{{APP_NAME}}"
  >
    <Heading
      :style="{
        margin: '0 0 16px 0',
        fontSize: '20px',
        fontWeight: 600,
        color: '#f3f4f6',
      }"
    >
      Verify your email address
    </Heading>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Hi <Raw>{{USER_NAME}}</Raw>,
    </Text>

    <Text :style="{ margin: '0 0 24px 0', color: '#d1d5db', fontSize: '14px' }">
      Thank you for signing up for <Raw>{{APP_NAME}}</Raw>. Please verify your email address by clicking the button below:
    </Text>

    <div :style="{ textAlign: 'center', margin: '32px 0' }">
      <EmailButton href="{{VERIFICATION_URL}}">Verify Email Address</EmailButton>
    </div>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Or copy and paste this link into your browser:
    </Text>

    <Text :style="linkBox">
      <Raw>{{VERIFICATION_URL}}</Raw>
    </Text>

    <Text :style="{ margin: '0 0 16px 0', color: '#9ca3af', fontSize: '13px' }">
      This link will expire in <Raw>{{EXPIRES_HOURS}}</Raw> hours.
    </Text>

    <Text :style="{ margin: '24px 0 0 0', color: '#9ca3af', fontSize: '13px' }">
      If you didn't create an account with <Raw>{{APP_NAME}}</Raw>, you can safely ignore this email.
    </Text>
  </EmailLayout>
</template>