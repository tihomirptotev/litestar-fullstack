<script setup lang="ts">
/**
 * AuditLogTable — Nuxt port of `components/admin/audit-log-table.tsx`.
 * Paginated audit log with filter inputs for search / action / actor /
 * target / date range.
 */
import { type AuditLogEntry, adminListAuditLogs } from "#shared/api/sdk.gen"

const PAGE_SIZE = 50

const page = ref(1)
const search = ref("")
const action = ref("")
const actorId = ref("")
const targetType = ref("")
const createdAfter = ref("")
const createdBefore = ref("")

type AuditResult = { items: AuditLogEntry[]; total: number }
const { data, status } = await useAsyncData<AuditResult>(
  "admin-audit-logs",
  async () => {
    const toDate = (value: string) => (value ? new Date(value).toISOString() : undefined)
    const response = await adminListAuditLogs({
      query: {
        currentPage: page.value,
        pageSize: PAGE_SIZE,
        searchString: search.value || undefined,
        searchIgnoreCase: true,
        actionIn: action.value ? [action.value] : undefined,
        actorIdIn: actorId.value ? [actorId.value] : undefined,
        targetTypeIn: targetType.value ? [targetType.value] : undefined,
        createdAfter: toDate(createdAfter.value),
        createdBefore: toDate(createdBefore.value),
      },
    })
    return { items: response.data?.items ?? [], total: response.data?.total ?? 0 }
  },
  { watch: [page, search, action, actorId, targetType, createdAfter, createdBefore] },
)

const items = computed(() => data.value?.items ?? [])
const total = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const isLoading = computed(() => status.value === "pending")

const handleFilter = () => {
  page.value = 1
}

const formatDetails = (entry: AuditLogEntry) => {
  if (!entry.details) return ""
  try {
    const parsed: unknown = JSON.parse(entry.details)
    return typeof parsed === "string" ? parsed : JSON.stringify(parsed)
  } catch {
    return entry.details
  }
}

const formatTime = (value: string) => new Date(value).toLocaleString()
</script>

<template>
  <UCard>
    <template #header>
      <h2 class="font-semibold">Audit log</h2>
    </template>

    <div class="mb-4 grid gap-2 md:grid-cols-6">
      <UInput
        v-model="search"
        placeholder="Search..."
        class="md:col-span-2"
        @update:model-value="handleFilter"
      />
      <UInput
        v-model="action"
        placeholder="Action"
        @update:model-value="handleFilter"
      />
      <UInput
        v-model="actorId"
        placeholder="Actor ID"
        @update:model-value="handleFilter"
      />
      <UInput
        v-model="targetType"
        placeholder="Target type"
        @update:model-value="handleFilter"
      />
      <div class="grid grid-cols-2 gap-2 md:col-span-2 md:grid-cols-2">
        <UInput
          v-model="createdAfter"
          type="date"
          @update:model-value="handleFilter"
        />
        <UInput
          v-model="createdBefore"
          type="date"
          @update:model-value="handleFilter"
        />
      </div>
    </div>

    <div
      v-if="isLoading"
      class="space-y-2"
    >
      <USkeleton
        v-for="n in 6"
        :key="n"
        class="h-12 w-full"
      />
    </div>

    <div
      v-else-if="items.length === 0"
      class="py-6 text-center text-sm text-muted-foreground"
    >
      No audit entries found.
    </div>

    <div
      v-else
      class="overflow-x-auto"
    >
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border/60 text-left text-muted-foreground">
            <th class="py-2 pr-4 font-medium">Action</th>
            <th class="py-2 pr-4 font-medium">Actor</th>
            <th class="py-2 pr-4 font-medium">Target</th>
            <th class="py-2 pr-4 font-medium">IP</th>
            <th class="py-2 font-medium">When</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in items"
            :key="entry.id"
            class="border-b border-border/40 align-top last:border-0"
          >
            <td class="py-2.5 pr-4">
              <p class="font-medium">{{ entry.action }}</p>
              <p
                v-if="formatDetails(entry)"
                class="max-w-xs truncate text-xs text-muted-foreground"
              >
                {{ formatDetails(entry) }}
              </p>
            </td>
            <td class="py-2.5 pr-4 text-muted-foreground">{{ entry.actorEmail || "System" }}</td>
            <td class="py-2.5 pr-4 text-muted-foreground">{{ entry.targetLabel || entry.targetType }}</td>
            <td class="py-2.5 pr-4 font-mono text-xs text-muted-foreground">{{ entry.ipAddress }}</td>
            <td class="py-2.5 text-muted-foreground">{{ formatTime(entry.createdAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <template #footer>
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <span>{{ total }} entr{{ total === 1 ? "y" : "ies" }}</span>
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