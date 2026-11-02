<script setup lang="ts">
/**
 * Team Invitation Email Template — port of `src/emails/team-invitation.tsx` to Maizzle.
 *
 * Placeholders (substituted by Python `str.replace`, keep literal!):
 * - {{APP_NAME}} - Application name
 * - {{INVITER_NAME}} - Name of the person who sent the invitation
 * - {{TEAM_NAME}} - Name of the team
 * - {{INVITATION_URL}} - Team invitation link
 */
import EmailButton from "../components/Button.vue"
import EmailLayout from "../components/EmailLayout.vue"

const teamBox = {
  margin: "0 0 24px 0",
  padding: "16px",
  backgroundColor: "#1c2237",
  borderRadius: "8px",
  borderLeft: "4px solid #FFB000",
}

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
    preview="You've been invited to join a team"
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
      You've been invited to join a team
    </Heading>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Hello,
    </Text>

    <Text :style="{ margin: '0 0 24px 0', color: '#d1d5db', fontSize: '14px' }">
      <Raw>{{INVITER_NAME}}</Raw> has invited you to join the team <strong><Raw>{{TEAM_NAME}}</Raw></strong> on <Raw>{{APP_NAME}}</Raw>.
    </Text>

    <div :style="teamBox">
      <Text
        :style="{
          margin: '0',
          color: '#f3f4f6',
          fontSize: '14px',
          fontWeight: 500,
        }"
      >
        Team: <Raw>{{TEAM_NAME}}</Raw>
      </Text>
      <Text
        :style="{
          margin: '8px 0 0 0',
          color: '#d1d5db',
          fontSize: '13px',
        }"
      >
        Invited by: <Raw>{{INVITER_NAME}}</Raw>
      </Text>
    </div>

    <div :style="{ textAlign: 'center', margin: '32px 0' }">
      <EmailButton
        href="{{INVITATION_URL}}"
        variant="success"
      >
        Accept Invitation
      </EmailButton>
    </div>

    <Text :style="{ margin: '0 0 16px 0', color: '#d1d5db', fontSize: '14px' }">
      Or copy and paste this link into your browser:
    </Text>

    <Text :style="linkBox">
      <Raw>{{INVITATION_URL}}</Raw>
    </Text>

    <Text :style="{ margin: '24px 0 0 0', color: '#9ca3af', fontSize: '13px' }">
      If you don't want to join this team, you can safely ignore this email.
    </Text>
  </EmailLayout>
</template>