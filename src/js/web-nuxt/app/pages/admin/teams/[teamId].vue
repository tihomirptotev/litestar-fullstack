<script setup lang="ts">
/**
 * Admin team detail — Nuxt port of `routes/_app/admin/teams/$teamId.tsx`.
 * View/update/delete a single team as a superuser.
 */
import { type AdminTeamDetail, adminDeleteTeam, adminGetTeam, adminUpdateTeam } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

const route = useRoute()
const toast = useToast()
const teamId = computed(() => String(route.params.teamId))

const { data, status, refresh } = await useAsyncData<AdminTeamDetail | null>(`admin-team-${teamId.value}`, async () => {
  const response = await adminGetTeam({ path: { team_id: teamId.value } })
  return response.data ?? null
})
const team = computed(() => data.value)
const isLoading = computed(() => status.value === "pending")
const isError = computed(() => status.value === "error")

const editOpen = ref(false)
const editName = ref("")
const editDescription = ref("")
const editPending = ref(false)

const openEdit = () => {
  if (!team.value) return
  editName.value = team.value.name
  editDescription.value = team.value.description || ""
  editOpen.value = true
}

const handleUpdate = async () => {
  if (!editName.value.trim()) {
    toast.add({ title: "Team name is required", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  editPending.value = true
  try {
    await adminUpdateTeam({
      path: { team_id: teamId.value },
      body: {
        name: editName.value.trim(),
        description: editDescription.value.trim() || undefined,
      },
    })
    toast.add({ title: "Team updated", color: "success", icon: "i-lucide-circle-check" })
    editOpen.value = false
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to update team", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    editPending.value = false
  }
}

const handleToggleActive = async () => {
  if (!team.value) return
  try {
    await adminUpdateTeam({
      path: { team_id: teamId.value },
      body: { is_active: !team.value.isActive },
    })
    toast.add({ title: team.value.isActive ? "Team disabled" : "Team activated", color: "success", icon: "i-lucide-circle-check" })
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to update team", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  }
}

const deletePending = ref(false)

const handleDelete = async () => {
  if (!confirm("Delete this team permanently? This cannot be undone.")) return
  deletePending.value = true
  try {
    await adminDeleteTeam({ path: { team_id: teamId.value } })
    toast.add({ title: "Team deleted", color: "success", icon: "i-lucide-circle-check" })
    navigateTo("/admin/teams")
  } catch (error) {
    toast.add({ title: "Unable to delete team", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
    deletePending.value = false
  }
}
</script>

<script lang="ts">
definePageMeta({
  layout: "app",
  middleware: ["auth", "admin"],
})
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h1 class="text-2xl font-semibold">Team details</h1>
      <p class="text-sm text-muted-foreground">Inspect and manage a single team.</p>
    </div>
    <AdminNav />

    <div v-if="isLoading">
      <USkeleton class="h-64 w-full" />
    </div>

    <UCard v-else-if="isError || !team">
      <p class="text-sm text-muted-foreground">Team not found.</p>
      <UButton
        to="/admin/teams"
        variant="link"
        class="mt-2 p-0"
      >
        Back to teams
      </UButton>
    </UCard>

    <template v-else>
      <UCard>
        <template #header>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="space-y-1">
              <h2 class="font-semibold">{{ team.name }}</h2>
              <p class="text-sm text-muted-foreground">{{ team.slug }}</p>
            </div>
            <UBadge
              :color="team.isActive ? 'success' : 'error'"
              variant="subtle"
            >
              {{ team.isActive ? "Active" : "Disabled" }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p class="text-sm text-muted-foreground">Description</p>
              <p>{{ team.description || "—" }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Owner</p>
              <p>{{ team.ownerEmail }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Members</p>
              <p>{{ team.memberCount }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Updated</p>
              <p>{{ new Date(team.updatedAt).toLocaleString() }}</p>
            </div>
          </div>

          <div>
            <p class="mb-2 text-sm font-medium">Members</p>
            <div
              v-if="team.members.length === 0"
              class="text-sm text-muted-foreground"
            >
              No members.
            </div>
            <div class="space-y-2">
              <div
                v-for="member in team.members"
                :key="member.user.id"
                class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/60 px-3 py-2"
              >
                <div class="min-w-0">
                  <p class="truncate font-medium">{{ member.user.name || member.user.email }}</p>
                  <p class="truncate text-sm text-muted-foreground">{{ member.user.email }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <UBadge
                    v-if="member.isOwner"
                    color="primary"
                    variant="subtle"
                  >
                    Owner
                  </UBadge>
                  <UBadge
                    color="neutral"
                    variant="subtle"
                  >
                    {{ member.role }}
                  </UBadge>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <UButton
              variant="outline"
              color="neutral"
              @click="openEdit"
            >
              Edit team
            </UButton>
            <UButton
              variant="outline"
              :color="team.isActive ? 'error' : 'primary'"
              @click="handleToggleActive"
            >
              {{ team.isActive ? "Disable team" : "Activate team" }}
            </UButton>
            <UButton
              color="error"
              variant="outline"
              :loading="deletePending"
              @click="handleDelete"
            >
              Delete team
            </UButton>
          </div>
        </div>
      </UCard>
    </template>

    <UModal
      v-model:open="editOpen"
      title="Edit team"
      description="Update the team name and description."
    >
      <template #body>
        <div class="space-y-4">
          <UFormField label="Name">
            <UInput
              v-model="editName"
              class="w-full"
            />
          </UFormField>
          <UFormField label="Description">
            <UTextarea
              v-model="editDescription"
              :rows="3"
              class="w-full"
            />
          </UFormField>
        </div>
      </template>
      <template #footer>
        <UButton
          :loading="editPending"
          @click="handleUpdate"
        >
          Save changes
        </UButton>
      </template>
    </UModal>
  </div>
</template>