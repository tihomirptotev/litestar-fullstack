<script setup lang="ts">
/**
 * UserTable — Nuxt port of `components/admin/user-table.tsx`.
 * Paginated admin user list with search; link to per-user detail.
 */
import { type AdminUserSummary, adminListUsers } from "#shared/api/sdk.gen"

const PAGE_SIZE = 25

const search = ref("")
const page = ref(1)
type UsersResult = { items: AdminUserSummary[]; total: number }
const { data, status } = await useAsyncData<UsersResult>(
  "admin-users",
  async () => {
    const response = await adminListUsers({
      query: { currentPage: page.value, pageSize: PAGE_SIZE, searchString: search.value || undefined, searchIgnoreCase: true },
    })
    return { items: response.data?.items ?? [], total: response.data?.total ?? 0 }
  },
  { watch: [page, search] },
)

const items = computed(() => data.value?.items ?? [])
const total = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const isLoading = computed(() => status.value === "pending")

const handleSearch = () => {
  page.value = 1
}

const formatStatus = (user: AdminUserSummary) => {
  if (!user.isActive) return "Disabled"
  if (!user.isVerified) return "Unverified"
  return "Active"
}
const statusColor = (user: AdminUserSummary) => (!user.isActive ? "error" : user.isVerified ? "success" : "warning")
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="font-semibold">Users</h2>
        <UInput
          v-model="search"
          placeholder="Search users..."
          class="w-64"
          icon="i-lucide-search"
          @update:model-value="handleSearch"
        />
      </div>
    </template>

    <div
      v-if="isLoading"
      class="space-y-2"
    >
      <USkeleton
        v-for="n in 6"
        :key="n"
        class="h-10 w-full"
      />
    </div>

    <div
      v-else-if="items.length === 0"
      class="py-6 text-center text-sm text-muted-foreground"
    >
      No users found.
    </div>

    <div
      v-else
      class="overflow-x-auto"
    >
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border/60 text-left text-muted-foreground">
            <th class="py-2 pr-4 font-medium">Name</th>
            <th class="py-2 pr-4 font-medium">Email</th>
            <th class="py-2 pr-4 font-medium">Joined</th>
            <th class="py-2 pr-4 font-medium">Logins</th>
            <th class="py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in items"
            :key="user.id"
            class="border-b border-border/40 last:border-0"
          >
            <td class="py-2.5 pr-4">
              <ULink
                :to="`/admin/users/${user.id}`"
                class="font-medium hover:underline"
              >
                {{ user.name || user.email }}
              </ULink>
            </td>
            <td class="py-2.5 pr-4 text-muted-foreground">{{ user.email }}</td>
            <td class="py-2.5 pr-4 text-muted-foreground">{{ new Date(user.createdAt).toLocaleDateString() }}</td>
            <td class="py-2.5 pr-4 text-muted-foreground">{{ user.loginCount }}</td>
            <td class="py-2.5">
              <UBadge
                :color="statusColor(user)"
                variant="subtle"
              >
                {{ formatStatus(user) }}
              </UBadge>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <template #footer>
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <span>{{ total }} user{{ total === 1 ? "" : "s" }}</span>
        <div class="flex items-center gap-2">
          <UBadge
            color="neutral"
            variant="subtle"
          >
            Page {{ page }} / {{ totalPages }}
          </UBadge>
          <UButton
            variant="outline"
            color="neutral"
            size="sm"
            icon="i-lucide-chevron-left"
            :disabled="page <= 1"
            @click="page -= 1"
          >
            Prev
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="sm"
            trailing-icon="i-lucide-chevron-right"
            :disabled="page >= totalPages"
            @click="page += 1"
          >
            Next
          </UButton>
        </div>
      </div>
    </template>
  </UCard>
</template>