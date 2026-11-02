<script setup lang="ts">
/**
 * Admin workspaces — Nuxt port of `routes/_app/admin/workspaces/index.tsx`.
 */
useHead({ title: "Workspaces" })
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
      <h1 class="text-2xl font-semibold">Workspaces</h1>
      <p class="text-sm text-muted-foreground">Manage platform workspaces.</p>
    </div>
    <AdminNav />
    <AdminWorkspaceTable />
  </div>
</template>