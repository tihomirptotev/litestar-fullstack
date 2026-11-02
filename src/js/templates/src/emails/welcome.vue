<script setup lang="ts">
/**
 * Welcome Email Template — port of `src/emails/welcome.tsx` to Maizzle.
 *
 * Placeholders (substituted by Python `str.replace`, keep literal!):
 * - {{APP_NAME}} - Application name
 * - {{USER_NAME}} - User's display name
 * - {{LOGIN_URL}} - Login page URL
 */
import EmailButton from "../components/Button.vue"
import EmailLayout from "../components/EmailLayout.vue"

const listStyle = {
  margin: "0 0 24px 0",
  paddingLeft: "20px",
  color: "#d1d5db",
}
const listItemStyle = {
  marginBottom: "8px",
  fontSize: "14px",
}
</script>

<template>
  <EmailLayout
    preview="Welcome to {{APP_NAME}}"
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
      <Raw>Welcome to {{APP_NAME}}!</Raw>
    </Heading>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Hi <Raw>{{USER_NAME}}</Raw>,
    </Text>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Your email has been verified and your account is now fully activated. We're excited to have you on board!
    </Text>

    <Text :style="{ margin: '0 0 24px 0', color: '#d1d5db', fontSize: '14px' }">
      Here's what you can do next:
    </Text>

    <ul :style="listStyle">
      <li :style="listItemStyle">Complete your profile settings</li>
      <li :style="listItemStyle">Enable two-factor authentication for extra security</li>
      <li :style="listItemStyle">Create or join a workspace</li>
    </ul>

    <div :style="{ textAlign: 'center', margin: '32px 0' }">
      <EmailButton href="{{LOGIN_URL}}">Get Started</EmailButton>
    </div>

    <Text :style="{ margin: '24px 0 0 0', color: '#9ca3af', fontSize: '13px' }">
      If you have any questions, feel free to reach out to our support workspace.
    </Text>
  </EmailLayout>
</template>