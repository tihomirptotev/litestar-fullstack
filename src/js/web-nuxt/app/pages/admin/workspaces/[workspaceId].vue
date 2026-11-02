<script setup lang="ts">
/**
 * Admin workspace detail — Nuxt port of `routes/_app/admin/workspaces/$workspaceId.tsx`.
 * View/update/delete a single workspace as a superuser.
 */
import { type AdminWorkspaceDetail, adminDeleteWorkspace, adminGetWorkspace, adminUpdateWorkspace } from "#shared/api/sdk.gen"
import { apiErrorMessage } from "~/composables/api"

const route = useRoute()
const toast = useToast()
const workspaceId = computed(() => String(route.params.workspaceId))

const { data, status, refresh } = await useAsyncData<AdminWorkspaceDetail | null>(`admin-workspace-${workspaceId.value}`, async () => {
  const response = await adminGetWorkspace({ path: { workspace_id: workspaceId.value } })
  return response.data ?? null
})
const workspace = computed(() => data.value)
const isLoading = computed(() => status.value === "pending")
const isError = computed(() => status.value === "error")

const editOpen = ref(false)
const editName = ref("")
const editDescription = ref("")
const editPending = ref(false)

const openEdit = () => {
  if (!workspace.value) return
  editName.value = workspace.value.name
  editDescription.value = workspace.value.description || ""
  editOpen.value = true
}

const handleUpdate = async () => {
  if (!editName.value.trim()) {
    toast.add({ title: "Workspace name is required", color: "error", icon: "i-lucide-circle-alert" })
    return
  }
  editPending.value = true
  try {
    await adminUpdateWorkspace({
      path: { workspace_id: workspaceId.value },
      body: {
        name: editName.value.trim(),
        description: editDescription.value.trim() || undefined,
      },
    })
    toast.add({ title: "Workspace updated", color: "success", icon: "i-lucide-circle-check" })
    editOpen.value = false
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to update workspace", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    editPending.value = false
  }
}

const handleToggleActive = async () => {
  if (!workspace.value) return
  try {
    await adminUpdateWorkspace({
      path: { workspace_id: workspaceId.value },
      body: { is_active: !workspace.value.isActive },
    })
    toast.add({ title: workspace.value.isActive ? "Workspace disabled" : "Workspace activated", color: "success", icon: "i-lucide-circle-check" })
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to update workspace", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  }
}

const deletePending = ref(false)

const handleDelete = async () => {
  if (!confirm("Delete this workspace permanently? This cannot be undone.")) return
  deletePending.value = true
  try {
    await adminDeleteWorkspace({ path: { workspace_id: workspaceId.value } })
    toast.add({ title: "Workspace deleted", color: "success", icon: "i-lucide-circle-check" })
    navigateTo("/admin/workspaces")
  } catch (error) {
    toast.add({ title: "Unable to delete workspace", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
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
      <h1 class="text-2xl font-semibold">Workspace details</h1>
      <p class="text-sm text-muted-foreground">Inspect and manage a single workspace.</p>
    </div>
    <AdminNav />

    <div v-if="isLoading">
      <USkeleton class="h-64 w-full" />
    </div>

    <UCard v-else-if="isError || !workspace">
      <p class="text-sm text-muted-foreground">Workspace not found.</p>
      <UButton
        to="/admin/workspaces"
        variant="link"
        class="mt-2 p-0"
      >
        Back to workspaces
      </UButton>
    </UCard>

    <template v-else>
      <UCard>
        <template #header>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="space-y-1">
              <h2 class="font-semibold">{{ workspace.name }}</h2>
              <p class="text-sm text-muted-foreground">{{ workspace.slug }}</p>
            </div>
            <UBadge
              :color="workspace.isActive ? 'success' : 'error'"
              variant="subtle"
            >
              {{ workspace.isActive ? "Active" : "Disabled" }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p class="text-sm text-muted-foreground">Description</p>
              <p>{{ workspace.description || "—" }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Owner</p>
              <p>{{ workspace.ownerEmail }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Members</p>
              <p>{{ workspace.memberCount }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Updated</p>
              <p>{{ new Date(workspace.updatedAt).toLocaleString() }}</p>
            </div>
          </div>

          <div>
            <p class="mb-2 text-sm font-medium">Members</p>
            <div
              v-if="workspace.members.length === 0"
              class="text-sm text-muted-foreground"
            >
              No members.
            </div>
            <div class="space-y-2">
              <div
                v-for="member in workspace.members"
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
              Edit workspace
            </UButton>
            <UButton
              variant="outline"
              :color="workspace.isActive ? 'error' : 'primary'"
              @click="handleToggleActive"
            >
              {{ workspace.isActive ? "Disable workspace" : "Activate workspace" }}
            </UButton>
            <UButton
              color="error"
              variant="outline"
              :loading="deletePending"
              @click="handleDelete"
            >
              Delete workspace
            </UButton>
          </div>
        </div>
      </UCard>
    </template>

    <UModal
      v-model:open="editOpen"
      title="Edit workspace"
      description="Update the workspace name and description."
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