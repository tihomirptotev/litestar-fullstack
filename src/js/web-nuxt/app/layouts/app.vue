<script setup lang="ts">
/**
 * Authenticated app layout — Nuxt port of the React app's `_app.tsx`
 * pathless layout + `app-layout.tsx`.
 * The `auth` route middleware replicates the `beforeLoad` guard.
 */
import { useAuth } from "~/composables/useAuth"

definePageMeta({
  middleware: "auth",
})

const auth = useAuth()
const route = useRoute()

/** Header title (mirrors the React app's pathname-based eyebrow/title map). */
const title = computed(() => {
  const path = route.path
  if (path === "/home") return "Overview"
  if (path === "/teams/new") return "Create team"
  if (path === "/teams") return "Workspace"
  if (path === "/profile") return "Account"
  if (path.startsWith("/admin")) return "Operations"
  if (path.startsWith("/teams/")) return "Workspace"
  return "Home"
})
</script>

<template>
  <UDashboardGroup unit="rem">
    <AppSidebar />

    <UDashboardPanel id="app-content">
      <template #header>
        <UDashboardNavbar :title="title">
          <template #leading>
            <UDashboardSidebarCollapse />
          </template>

          <template #right>
            <UBadge
              v-if="auth.currentTeam.value && route.path !== '/teams/new'"
              color="neutral"
              variant="subtle"
              size="sm"
              class="gap-1.5"
            >
              <UIcon name="i-lucide-users" />
              <span class="text-xs">{{ auth.currentTeam.value.name }}</span>
            </UBadge>
          </template>
        </UDashboardNavbar>
      </template>

      <template #body>
        <slot />
      </template>
    </UDashboardPanel>
  </UDashboardGroup>
</template>