<script setup lang="ts">
/**
 * Accept invitation page — Nuxt port of the React app's
 * `routes/_app/workspaces/$workspaceId/invitations/$invitationId/accept.tsx`.
 * Accept / decline invitation card with status state machine.
 */
import { acceptWorkspaceInvitation, getWorkspace, rejectWorkspaceInvitation, type Workspace } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

definePageMeta({ layout: "app" })

const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId))
const invitationId = computed(() => String(route.params.invitationId))
const toast = useToast()

type Status = "pending" | "accepting" | "declining" | "accepted" | "declined" | "error"
const status = ref<Status>("pending")
const errorMessage = ref<string | null>(null)

// Optionally fetch workspace info for display
const { data: workspace, status: workspaceStatus } = await useAsyncData<Workspace | null>(`workspace-${workspaceId.value}`, async () => {
  const response = await getWorkspace({ path: { workspace_id: workspaceId.value } })
  return response.data ?? null
})
const isWorkspaceLoading = computed(() => workspaceStatus.value === "pending")

const accept = async () => {
  status.value = "accepting"
  errorMessage.value = null
  try {
    await acceptWorkspaceInvitation({ path: { workspace_id: workspaceId.value, invitation_id: invitationId.value } })
    status.value = "accepted"
    toast.add({ title: "You've joined the workspace!", color: "success", icon: "i-lucide-circle-check" })
    // Navigate to the workspace page after a short delay
    setTimeout(() => {
      navigateTo(`/workspaces/${workspaceId.value}`)
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
    await rejectWorkspaceInvitation({ path: { workspace_id: workspaceId.value, invitation_id: invitationId.value } })
    status.value = "declined"
    toast.add({ title: "Invitation declined", color: "success", icon: "i-lucide-circle-check" })
    // Navigate to workspaces list after a short delay
    setTimeout(() => {
      navigateTo("/workspaces")
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

useHead({ title: "Workspace Invitation — Litestar Fullstack" })
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
            {{ status === "accepted" ? "Welcome to the workspace!" : status === "declined" ? "Invitation declined" : "Workspace Invitation" }}
          </h2>
          <p class="text-sm text-muted-foreground">
            <template v-if="status === 'accepted'"> You're now a member. Redirecting... </template>
            <template v-else-if="status === 'declined'"> You won't be added to this workspace. </template>
            <template v-else-if="isWorkspaceLoading"> Loading invitation details... </template>
            <template v-else-if="workspace">
              You've been invited to join <strong>{{ workspace.name }}</strong>
            </template>
            <template v-else> You've been invited to join a workspace </template>
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
            <p class="text-sm text-muted-foreground">{{ status === "accepting" ? "Joining workspace..." : "Declining invitation..." }}</p>
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