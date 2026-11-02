<script setup lang="ts">
/**
 * Team detail page — Nuxt port of the React app's
 * `routes/_app/teams/$teamId.tsx`.
 * Members card + pending invitations + overview card; invite dialog for
 * users who can manage members.
 */
import { computed, ref, watch } from "vue"
import { deleteTeamInvitation, getTeam, listTeamInvitations, removeMemberFromTeam, type Team, type TeamInvitation, type TeamMember } from "#shared/api/sdk.gen"
import { useAuth } from "~/composables/useAuth"

definePageMeta({ layout: "app" })

const route = useRoute()
const teamId = computed(() => String(route.params.teamId))
const auth = useAuth()

// --- Team fetch -------------------------------------------------------------
const {
  data: team,
  error: teamError,
  status: teamStatus,
} = await useAsyncData<Team | null, unknown>(`team-${teamId.value}`, async () => {
  const response = await getTeam({ path: { team_id: teamId.value } })
  return response.data ?? null
})

const isTeamLoading = computed(() => teamStatus.value === "pending")
const isTeamError = computed(() => Boolean(teamError.value))

// Keep the auth store's current team in sync with the viewed team.
watch(
  team,
  (value) => {
    if (value && value.id !== auth.currentTeam.value?.id) {
      auth.setCurrentTeam(value)
    }
  },
  { immediate: true },
)

// --- Invitations ------------------------------------------------------------
const { data: invitationsData, refresh: refreshInvitations } = await useAsyncData<TeamInvitation[]>(
  `teamInvitations-${teamId.value}`,
  async () => {
    const response = await listTeamInvitations({ path: { team_id: teamId.value } })
    return response.data?.items ?? []
  },
  { default: () => [] },
)

const pendingInvitations = computed(() => invitationsData.value.filter((inv) => !inv.isAccepted))

const cancelInvitation = async (invitationId: string) => {
  await deleteTeamInvitation({ path: { team_id: teamId.value, invitation_id: invitationId } })
  await refreshInvitations()
}

// --- Members ---------------------------------------------------------------
const removingEmail = ref<string | null>(null)

const removeMember = async (memberEmail: string) => {
  removingEmail.value = memberEmail
  try {
    await removeMemberFromTeam({ path: { team_id: teamId.value }, body: { userName: memberEmail } })
    await refreshNuxtData(`team-${teamId.value}`)
  } finally {
    removingEmail.value = null
  }
}

const members = computed<TeamMember[]>(() => team.value?.members ?? [])
const owner = computed(() => members.value.find((member) => member.isOwner))
const isOwner = computed(() => owner.value?.userId === auth.user.value?.id)
const canManageMembers = computed(
  () => isOwner.value || Boolean(auth.user.value?.isSuperuser) || members.value.some((member) => member.userId === auth.user.value?.id && member.role === "ADMIN"),
)

const canRemoveMember = (member: TeamMember) => {
  // Cannot remove the owner (they must transfer ownership first)
  if (member.isOwner) return false
  // Cannot remove yourself unless you're superuser
  if (member.userId === auth.user.value?.id && !auth.user.value?.isSuperuser) return false
  return canManageMembers.value
}

useHead({ title: () => `${team.value?.name ?? "Team"} — Litestar Fullstack` })
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <!-- Loading state -->
      <div
        v-if="isTeamLoading"
        class="text-muted-foreground"
      >
        Loading team...
      </div>

      <!-- Error / not found -->
      <div
        v-else-if="isTeamError || !team"
        class="text-muted-foreground"
      >
        {{ isTeamError ? "We couldn't load this team yet. Try refreshing." : "Team not found" }}
      </div>

      <template v-else>
        <PageHeader
          eyebrow="Teams"
          :title="team.name"
          :description="team.description || 'No description provided.'"
        >
          <template #actions>
            <div class="flex items-center gap-3">
              <UButton
                variant="outline"
                color="neutral"
                size="sm"
                icon="i-lucide-arrow-left"
                to="/teams"
              >
                Back
              </UButton>
              <TeamsInviteMemberDialog
                v-if="canManageMembers"
                :team-id="teamId"
              />
            </div>
          </template>
        </PageHeader>

        <div class="grid gap-4 md:grid-cols-[1.1fr_0.9fr]">
          <!-- Members card -->
          <UCard class="border-border/60 bg-card/80 shadow-md shadow-primary/10">
            <template #header>
              <h2 class="font-semibold">Members</h2>
            </template>
            <div class="space-y-3">
              <div
                v-for="member in members"
                :key="member.id"
                class="flex items-center justify-between rounded-xl border bg-background/60 p-3"
                :class="member.userId === auth.user.value?.id ? 'border-primary/30 bg-primary/5' : 'border-border/60'"
              >
                <div class="flex flex-col">
                  <div class="flex items-center gap-2">
                    <p class="font-medium text-foreground">{{ member.name ?? member.email }}</p>
                    <UBadge
                      v-if="member.userId === auth.user.value?.id"
                      variant="secondary"
                      class="text-[10px]"
                    >
                      You
                    </UBadge>
                    <UBadge
                      v-if="member.isOwner"
                      class="text-[10px]"
                    >
                      Owner
                    </UBadge>
                  </div>
                  <p class="text-sm text-muted-foreground">{{ member.email }}</p>
                </div>
                <div class="flex items-center gap-3">
                  <UBadge
                    variant="outline"
                    class="uppercase"
                  >
                    {{ member.role ?? "MEMBER" }}
                  </UBadge>
                  <UButton
                    v-if="canRemoveMember(member)"
                    variant="outline"
                    color="neutral"
                    size="sm"
                    :loading="removingEmail === member.email"
                    @click="removeMember(member.email)"
                  >
                    Remove
                  </UButton>
                </div>
              </div>
              <div
                v-if="members.length === 0"
                class="text-sm text-muted-foreground"
              >
                No members yet.
              </div>

              <!-- Pending invitations -->
              <template v-if="pendingInvitations.length > 0">
                <USeparator class="my-4" />
                <div class="space-y-2">
                  <p class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <UIcon
                      name="i-lucide-clock"
                      class="h-4 w-4"
                    />
                    Pending invitations
                  </p>
                  <div
                    v-for="invitation in pendingInvitations"
                    :key="invitation.id"
                    class="flex items-center justify-between rounded-lg border border-dashed border-border/60 bg-muted/30 p-3"
                  >
                    <div class="flex items-center gap-3">
                      <UIcon
                        name="i-lucide-mail"
                        class="h-4 w-4 text-muted-foreground"
                      />
                      <div>
                        <p class="text-sm font-medium">{{ invitation.email }}</p>
                        <p class="text-xs text-muted-foreground">Invited as {{ invitation.role.toLowerCase() }}</p>
                      </div>
                    </div>
                    <UButton
                      v-if="canManageMembers"
                      variant="ghost"
                      color="neutral"
                      size="sm"
                      icon="i-lucide-x"
                      aria-label="Cancel invitation"
                      @click="cancelInvitation(invitation.id)"
                    />
                  </div>
                </div>
              </template>
            </div>
          </UCard>

          <!-- Overview card -->
          <UCard class="border-border/60 bg-card/80 shadow-md shadow-primary/10">
            <template #header>
              <h2 class="font-semibold">Team overview</h2>
            </template>
            <div class="space-y-3 text-sm text-muted-foreground">
              <div class="flex justify-between text-foreground">
                <span>Member count</span>
                <UBadge variant="secondary">{{ members.length }}</UBadge>
              </div>
              <USeparator class="my-3" />
              <p>Use this space to track key links, environments, or runbooks for the team.</p>
            </div>
          </UCard>
        </div>
      </template>
    </PageContainer>
  </div>
</template>