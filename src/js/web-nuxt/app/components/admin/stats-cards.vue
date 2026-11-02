<script setup lang="ts">
/**
 * StatsCards — Nuxt port of `components/admin/stats-cards.tsx`.
 * Dashboard metric cards from `getDashboardStats`.
 */
import { getDashboardStats } from "#shared/api/sdk.gen"
import type { DashboardStats } from "#shared/api/types.gen"

const { data, status } = await useAsyncData<DashboardStats | null>("admin-dashboard-stats", async () => {
  const response = await getDashboardStats()
  return response.data ?? null
})
const isLoading = computed(() => status.value === "pending")

const stats = computed(() => data.value)

const metricClasses = ["text-primary", "text-success", "text-info", "text-warning", "text-error", "text-muted", "text-secondary"]
const cardMeta = computed(() => {
  if (!stats.value) return []
  return [
    { label: "Total users", value: stats.value.totalUsers, icon: "i-lucide-users" },
    { label: "Active users", value: stats.value.activeUsers, icon: "i-lucide-user-check" },
    { label: "Verified users", value: stats.value.verifiedUsers, icon: "i-lucide-mail-check" },
    { label: "New users (today)", value: stats.value.newUsersToday, icon: "i-lucide-user-plus" },
    { label: "New users (week)", value: stats.value.newUsersWeek, icon: "i-lucide-users" },
    { label: "Workspaces", value: stats.value.totalWorkspaces, icon: "i-lucide-users-round" },
    { label: "Events (today)", value: stats.value.eventsToday, icon: "i-lucide-activity" },
  ]
})
</script>

<template>
  <div
    v-if="isLoading"
    class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
  >
    <USkeleton class="h-28 w-full" />
    <USkeleton class="h-28 w-full" />
    <USkeleton class="h-28 w-full" />
    <USkeleton class="h-28 w-full" />
  </div>

  <div
    v-else-if="stats"
    class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
  >
    <UCard
      v-for="(item, index) in cardMeta"
      :key="item.label"
      class="min-w-0"
      :ui="{ body: 'p-4 sm:p-4' }"
    >
      <div class="flex items-center gap-3">
        <div class="rounded-lg border border-border/60 bg-muted/30 p-2.5">
          <UIcon
            :name="item.icon"
            :class="metricClasses[index % metricClasses.length]"
            class="h-5 w-5"
          />
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm text-muted-foreground">{{ item.label }}</p>
          <p class="text-2xl font-semibold">{{ item.value }}</p>
        </div>
      </div>
    </UCard>
  </div>
</template>