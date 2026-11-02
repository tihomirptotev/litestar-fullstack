<script setup lang="ts">
/**
 * Password Reset Confirmation Email Template — port of
 * `src/emails/password-reset-confirmation.tsx` to Maizzle.
 *
 * Placeholders (substituted by Python `str.replace`, keep literal!):
 * - {{APP_NAME}} - Application name
 * - {{USER_NAME}} - User's display name
 * - {{LOGIN_URL}} - Login page URL
 */
import EmailButton from "../components/Button.vue"
import EmailLayout from "../components/EmailLayout.vue"
</script>

<template>
  <EmailLayout
    preview="Your password has been reset"
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
      Password reset complete
    </Heading>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Hi <Raw>{{USER_NAME}}</Raw>,
    </Text>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Your password for <Raw>{{APP_NAME}}</Raw> has been successfully reset.
    </Text>

    <Text :style="{ margin: '0 0 24px 0', color: '#d1d5db', fontSize: '14px' }">
      If you did not make this change, please contact support immediately.
    </Text>

    <div :style="{ textAlign: 'center', margin: '32px 0' }">
      <EmailButton href="{{LOGIN_URL}}">Sign In</EmailButton>
    </div>

    <Text :style="{ margin: '24px 0 0 0', color: '#9ca3af', fontSize: '13px' }">
      For security, avoid reusing old passwords and consider enabling multi-factor authentication.
    </Text>
  </EmailLayout>
</template>