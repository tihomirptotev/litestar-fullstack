<script setup lang="ts">
/**
 * Accept invitation page — Nuxt port of the React app's
 * `routes/_app/teams/$teamId/invitations/$invitationId/accept.tsx`.
 * Accept / decline invitation card with status state machine.
 */
import { acceptTeamInvitation, getTeam, rejectTeamInvitation, type Team } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

definePageMeta({ layout: "app" })

const route = useRoute()
const teamId = computed(() => String(route.params.teamId))
const invitationId = computed(() => String(route.params.invitationId))
const toast = useToast()

type Status = "pending" | "accepting" | "declining" | "accepted" | "declined" | "error"
const status = ref<Status>("pending")
const errorMessage = ref<string | null>(null)

// Optionally fetch team info for display
const { data: team, status: teamStatus } = await useAsyncData<Team | null>(`team-${teamId.value}`, async () => {
  const response = await getTeam({ path: { team_id: teamId.value } })
  return response.data ?? null
})
const isTeamLoading = computed(() => teamStatus.value === "pending")

const accept = async () => {
  status.value = "accepting"
  errorMessage.value = null
  try {
    await acceptTeamInvitation({ path: { team_id: teamId.value, invitation_id: invitationId.value } })
    status.value = "accepted"
    toast.add({ title: "You've joined the team!", color: "success", icon: "i-lucide-circle-check" })
    // Navigate to the team page after a short delay
    setTimeout(() => {
      navigateTo(`/teams/${teamId.value}`)
    }, 1500)
  } catch (error) {
    status.value = "error"
    errorMessage.value = apiErrorMessage(error) || "Failed to accept invitation"
    toast.add({ title: "Failed to accept invitation", description: errorMessage.value, color: "error", icon: "i-lucide-circle-alert" })
  }
}

const decline = async () => {
  status.value = "declining"
  errorMessage.value = null
  try {
    await rejectTeamInvitation({ path: { team_id: teamId.value, invitation_id: invitationId.value } })
    status.value = "declined"
    toast.add({ title: "Invitation declined", color: "success", icon: "i-lucide-circle-check" })
    // Navigate to teams list after a short delay
    setTimeout(() => {
      navigateTo("/teams")
    }, 1500)
  } catch (error) {
    status.value = "error"
    errorMessage.value = apiErrorMessage(error) || "Failed to decline invitation"
    toast.add({ title: "Failed to decline invitation", description: errorMessage.value, color: "error", icon: "i-lucide-circle-alert" })
  }
}

const isPending = computed(() => status.value === "pending")
const isProcessing = computed(() => status.value === "accepting" || status.value === "declining")
const isComplete = computed(() => status.value === "accepted" || status.value === "declined")

useHead({ title: "Team Invitation — Litestar Fullstack" })
</script>

<template>
  <div class="flex flex-1 items-center justify-center">
    <PageContainer>
      <UCard class="w-full max-w-md border-border/60 bg-card/80 shadow-xl shadow-primary/15">
        <div class="text-center space-y-2">
          <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <UIcon
              v-if="status === 'accepted'"
              name="i-lucide-circle-check"
              class="h-6 w-6 text-success"
            />
            <UIcon
              v-else-if="status === 'declined'"
              name="i-lucide-circle-x"
              class="h-6 w-6 text-muted-foreground"
            />
            <UIcon
              v-else
              name="i-lucide-users"
              class="h-6 w-6 text-primary"
            />
          </div>
          <h2 class="text-lg font-semibold leading-none">
            {{ status === "accepted" ? "Welcome to the team!" : status === "declined" ? "Invitation declined" : "Team Invitation" }}
          </h2>
          <p class="text-sm text-muted-foreground">
            <template v-if="status === 'accepted'"> You're now a member. Redirecting... </template>
            <template v-else-if="status === 'declined'"> You won't be added to this team. </template>
            <template v-else-if="isTeamLoading"> Loading invitation details... </template>
            <template v-else-if="team">
              You've been invited to join <strong>{{ team.name }}</strong>
            </template>
            <template v-else> You've been invited to join a team </template>
          </p>
        </div>

        <div>
          <UAlert
            v-if="status === 'error' && errorMessage"
            class="mb-4"
            color="error"
            variant="subtle"
          >
            <UAlertDescription>{{ errorMessage }}</UAlertDescription>
          </UAlert>

          <div
            v-if="isProcessing"
            class="flex flex-col items-center space-y-3 py-4"
          >
            <UIcon
              name="i-lucide-loader-circle"
              class="h-8 w-8 animate-spin text-primary"
            />
            <p class="text-sm text-muted-foreground">{{ status === "accepting" ? "Joining team..." : "Declining invitation..." }}</p>
          </div>

          <div
            v-if="isComplete"
            class="flex flex-col items-center space-y-3 py-4"
          >
            <UIcon
              name="i-lucide-loader-circle"
              class="h-6 w-6 animate-spin text-muted-foreground"
            />
            <p class="text-sm text-muted-foreground">Redirecting...</p>
          </div>
        </div>

        <div
          v-if="isPending || status === 'error'"
          class="flex flex-col gap-2"
        >
          <UButton
            class="w-full"
            :disabled="isProcessing"
            @click="accept"
          >
            Accept Invitation
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            class="w-full"
            :disabled="isProcessing"
            @click="decline"
          >
            Decline
          </UButton>
        </div>
      </UCard>
    </PageContainer>
  </div>
</template>