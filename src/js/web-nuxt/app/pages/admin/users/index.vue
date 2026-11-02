<script setup lang="ts">
/**
 * Admin users — Nuxt port of `routes/_app/admin/users/index.tsx`.
 */
useHead({ title: "Users" })
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
      <h1 class="text-2xl font-semibold">Users</h1>
      <p class="text-sm text-muted-foreground">Manage platform users.</p>
    </div>
    <AdminNav />
    <AdminUserTable />
  </div>
</template>