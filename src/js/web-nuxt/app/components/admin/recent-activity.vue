<script setup lang="ts">
/**
 * RecentActivity — Nuxt port of `components/admin/recent-activity.tsx`.
 * Latest audit events from `getRecentActivity`.
 */
import { type ActivityLogEntry, getRecentActivity } from "#shared/api/sdk.gen"

const { data, status } = await useAsyncData<{ items: ActivityLogEntry[] }>("admin-recent-activity", async () => {
  const response = await getRecentActivity()
  return { items: response.data?.activities ?? [] }
})
const activities = computed(() => data.value?.items ?? [])
const isLoading = computed(() => status.value === "pending")
const isError = computed(() => status.value === "error")

const formatTime = (value: string) => new Date(value).toLocaleString()
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="font-semibold">Recent activity</h2>
        <UButton
          to="/admin/audit"
          variant="ghost"
          color="neutral"
          size="sm"
          trailing-icon="i-lucide-arrow-right"
        >
          Audit log
        </UButton>
      </div>
    </template>

    <div
      v-if="isLoading"
      class="space-y-2"
    >
      <USkeleton
        v-for="n in 4"
        :key="n"
        class="h-12 w-full"
      />
    </div>

    <p
      v-else-if="isError"
      class="text-sm text-muted-foreground"
    >
      Failed to load recent activity.
    </p>

    <p
      v-else-if="activities.length === 0"
      class="text-sm text-muted-foreground"
    >
      No recent activity.
    </p>

    <div
      v-else
      class="space-y-2"
    >
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/60 px-3 py-2"
      >
        <div class="min-w-0">
          <p class="truncate font-medium">{{ activity.action }}</p>
          <p
            v-if="activity.targetLabel"
            class="truncate text-sm text-muted-foreground"
          >
            {{ activity.targetLabel }}
          </p>
        </div>
        <div class="text-right text-xs text-muted-foreground">
          <p>{{ activity.actorEmail || "System" }}</p>
          <p>{{ formatTime(activity.createdAt) }}</p>
        </div>
      </div>
    </div>
  </UCard>
</template>