<script setup lang="ts">
/**
 * Admin dashboard — Nuxt port of `routes/_app/admin/index.tsx`.
 */
useHead({ title: "Admin" })
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
      <h1 class="text-2xl font-semibold">Dashboard</h1>
      <p class="text-sm text-muted-foreground">Platform overview and recent activity.</p>
    </div>
    <AdminNav />
    <div class="space-y-6">
      <AdminStatsCards />
      <AdminRecentActivity />
    </div>
  </div>
</template>