<script setup lang="ts">
/**
 * AdminNav — Nuxt port of `components/admin/admin-nav.tsx`.
 * Tab-strap between the admin routes; highlights the active one.
 */
const route = useRoute()

const active = (to: string) => (to === "/admin" ? route.path === to : route.path.startsWith(to))

const links = [
  { to: "/admin", label: "Dashboard", icon: "i-lucide-layout-dashboard" },
  { to: "/admin/users", label: "Users", icon: "i-lucide-users" },
  { to: "/admin/teams", label: "Teams", icon: "i-lucide-users-round" },
  { to: "/admin/audit", label: "Audit log", icon: "i-lucide-scroll-text" },
]
</script>

<template>
  <nav class="flex flex-wrap gap-2">
    <UButton
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      :variant="active(link.to) ? 'solid' : 'outline'"
      color="neutral"
      size="sm"
      :icon="link.icon"
    >
      {{ link.label }}
    </UButton>
  </nav>
</template>