<script setup lang="ts">
/**
 * Admin user detail — Nuxt port of `routes/_app/admin/users/$userId.tsx`.
 * View/update/delete a single user as a superuser.
 */
import { adminDeleteUser, adminGetUser, adminUpdateUser } from "#shared/api/sdk.gen"
import type { AdminUserDetail } from "#shared/api/types.gen"
import { apiErrorMessage } from "~/composables/api"

const route = useRoute()
const toast = useToast()
const userId = computed(() => String(route.params.userId))

const { data, status, refresh } = await useAsyncData<AdminUserDetail | null>(`admin-user-${userId.value}`, async () => {
  const response = await adminGetUser({ path: { user_id: userId.value } })
  return response.data ?? null
})
const user = computed(() => data.value)
const isLoading = computed(() => status.value === "pending")
const isError = computed(() => status.value === "error")

type AdminUserPatch = {
  is_active?: boolean
  is_superuser?: boolean
  is_verified?: boolean
}

const togglePending = ref(false)

const handleToggle = async (field: "is_active" | "is_superuser" | "is_verified") => {
  if (!user.value) return
  const current: Record<string, boolean | undefined> = {
    is_active: user.value.isActive,
    is_superuser: user.value.isSuperuser,
  }
  void current
  const newValue = field === "is_active" ? !user.value.isActive : field === "is_superuser" ? !user.value.isSuperuser : !user.value.isVerified
  togglePending.value = true
  try {
    const body: AdminUserPatch = { [field]: newValue }
    await adminUpdateUser({ path: { user_id: userId.value }, body })
    toast.add({ title: "User updated", color: "success", icon: "i-lucide-circle-check" })
    refresh()
  } catch (error) {
    toast.add({ title: "Unable to update user", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
  } finally {
    togglePending.value = false
  }
}

const deletePending = ref(false)

const handleDelete = async () => {
  if (!confirm("Delete this user permanently? This cannot be undone.")) return
  deletePending.value = true
  try {
    await adminDeleteUser({ path: { user_id: userId.value } })
    toast.add({ title: "User deleted", color: "success", icon: "i-lucide-circle-check" })
    navigateTo("/admin/users")
  } catch (error) {
    toast.add({ title: "Unable to delete user", description: apiErrorMessage(error) || "Please try again", color: "error", icon: "i-lucide-circle-alert" })
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
      <h1 class="text-2xl font-semibold">User details</h1>
      <p class="text-sm text-muted-foreground">Inspect and manage a single user.</p>
    </div>
    <AdminNav />

    <div v-if="isLoading">
      <USkeleton class="h-64 w-full" />
    </div>

    <UCard v-else-if="isError || !user">
      <p class="text-sm text-muted-foreground">User not found.</p>
      <UButton
        to="/admin/users"
        variant="link"
        class="mt-2 p-0"
      >
        Back to users
      </UButton>
    </UCard>

    <template v-else>
      <UCard>
        <template #header>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="space-y-1">
              <h2 class="font-semibold">{{ user.name || user.email }}</h2>
              <p class="text-sm text-muted-foreground">{{ user.email }}</p>
            </div>
            <UBadge
              :color="user.isActive ? 'success' : 'error'"
              variant="subtle"
            >
              {{ user.isActive ? "Active" : "Disabled" }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p class="text-sm text-muted-foreground">Username</p>
              <p>{{ user.username || "—" }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Joined</p>
              <p>{{ new Date(user.joinedAt || user.createdAt).toLocaleDateString() }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Password set</p>
              <p>{{ user.hasPassword ? "Yes" : "No" }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">MFA</p>
              <p>{{ user.isTwoFactorEnabled ? "Enabled" : "Disabled" }}</p>
            </div>
          </div>

          <div
            v-if="user.oauthAccounts && user.oauthAccounts.length > 0"
            class="rounded-lg border border-border/60 px-3 py-2"
          >
            <p class="text-sm font-medium">Linked accounts</p>
            <p class="text-sm text-muted-foreground">
              {{ user.oauthAccounts.map((account) => account.oauthName).join(", ") }}
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <UButton
              variant="outline"
              :color="user.isActive ? 'error' : 'primary'"
              :disabled="togglePending"
              @click="handleToggle('is_active')"
            >
              {{ user.isActive ? "Deactivate" : "Activate" }}
            </UButton>
            <UButton
              variant="outline"
              color="neutral"
              :disabled="togglePending"
              @click="handleToggle('is_superuser')"
            >
              {{ user.isSuperuser ? "Revoke superuser" : "Make superuser" }}
            </UButton>
            <UButton
              variant="outline"
              color="neutral"
              :disabled="togglePending"
              @click="handleToggle('is_verified')"
            >
              {{ user.isVerified ? "Unverify" : "Verify" }}
            </UButton>
            <UButton
              color="error"
              variant="outline"
              :loading="deletePending"
              @click="handleDelete"
            >
              Delete user
            </UButton>
          </div>
        </div>
      </UCard>
    </template>
  </div>
</template>