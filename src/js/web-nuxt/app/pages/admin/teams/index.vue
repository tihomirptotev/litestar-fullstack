<script setup lang="ts">
/**
 * Admin teams — Nuxt port of `routes/_app/admin/teams/index.tsx`.
 */
useHead({ title: "Teams" })
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
      <h1 class="text-2xl font-semibold">Teams</h1>
      <p class="text-sm text-muted-foreground">Manage platform teams.</p>
    </div>
    <AdminNav />
    <AdminTeamTable />
  </div>
</template>