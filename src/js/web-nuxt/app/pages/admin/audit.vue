<script setup lang="ts">
/**
 * Admin audit log — Nuxt port of `routes/_app/admin/audit.tsx`.
 */
useHead({ title: "Audit log" })
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
      <h1 class="text-2xl font-semibold">Audit log</h1>
      <p class="text-sm text-muted-foreground">Searchable trail of platform events.</p>
    </div>
    <AdminNav />
    <AdminAuditLogTable />
  </div>
</template>