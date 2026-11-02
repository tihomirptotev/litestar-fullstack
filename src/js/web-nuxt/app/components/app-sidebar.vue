<script setup lang="ts">
/**
 * App sidebar — Nuxt port of the React app's `app-sidebar.tsx`,
 * `nav-main.tsx`, `nav-projects.tsx`, `workspace-switcher.tsx` and `nav-user.tsx`
 * collapsed into one component using Nuxt UI's `UDashboardSidebar`.
 */
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui"
import { getAccessToken } from "#shared/api/config"
import { listWorkspaces } from "#shared/api/sdk.gen"
import type { Workspace, User } from "#shared/api/types.gen"
import { unwrapAs } from "~/composables/api"

const auth = useAuth()
const route = useRoute()
const toast = useToast()

// --- Workspaces fetch + store sync (mirrors the React useQuery + useEffect sync) ---
const workspacesData = ref<Workspace[]>([])
const workspacesLoading = ref(false)

const loadWorkspaces = async () => {
  if (!getAccessToken() && !auth.isAuthenticated.value) {
    return
  }
  workspacesLoading.value = true
  try {
    const data = await unwrapAs<unknown, unknown, { items?: Workspace[] }>(listWorkspaces())
    workspacesData.value = data.items ?? []
    auth.setWorkspaces(workspacesData.value)
  } catch {
    // Non-fatal — sidebar falls back to the store's workspace list.
  } finally {
    workspacesLoading.value = false
  }
}

onMounted(() => {
  loadWorkspaces()
})

watch(
  () => auth.isAuthenticated.value,
  (authenticated) => {
    if (authenticated) {
      loadWorkspaces()
    }
  },
)

// Keep local list in sync when workspaces change elsewhere (e.g. create workspace page).
watch(
  () => auth.workspaces.value.map((workspace: Workspace) => workspace.id).join("|"),
  (storeIds) => {
    const localIds = workspacesData.value.map((workspace) => workspace.id).join("|")
    if (storeIds !== localIds) {
      workspacesData.value = auth.workspaces.value
    }
  },
)

const workspaceOptions = computed<Workspace[]>(() => (workspacesData.value.length > 0 ? workspacesData.value : auth.workspaces.value))

// --- Navigation items ---
const navItems = computed<NavigationMenuItem[]>(() => {
  const items: NavigationMenuItem[] = [
    {
      label: "Home",
      icon: "i-lucide-house",
      to: "/home",
    },
    {
      label: "Workspaces",
      icon: "i-lucide-users",
      to: "/workspaces",
      children: [
        { label: "All workspaces", to: "/workspaces" },
        { label: "Create new", to: "/workspaces/new" },
      ],
    },
  ]
  if (auth.user.value?.isSuperuser) {
    items.push({
      label: "Admin",
      icon: "i-lucide-shield-check",
      to: "/admin",
    })
  }
  return items
})

const workspaceLinks = computed<NavigationMenuItem[]>(() =>
  workspaceOptions.value.map((workspace: Workspace) => ({
    label: workspace.name,
    icon: "i-lucide-users",
    to: `/workspaces/${workspace.id}`,
  })),
)

// --- Workspace switcher ---
const activeWorkspace = computed<Workspace | null>(() => {
  const { currentWorkspace } = auth
  if (currentWorkspace.value) {
    return workspaceOptions.value.find((workspace) => workspace.id === currentWorkspace.value?.id) ?? workspaceOptions.value[0] ?? null
  }
  return workspaceOptions.value[0] ?? null
})

const workspaceInitials = (name: string) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

const onWorkspaceSelect = (workspace: Workspace) => {
  auth.setCurrentWorkspace(workspace)
}

// --- User menu ---
const onLogout = async () => {
  await auth.logout()
  await navigateTo("/")
}

const userItems = computed<(DropdownMenuItem | { type: "label"; label: string })[]>(() => {
  const user: User | null = auth.user.value
  if (!user) {
    return []
  }
  return [
    { type: "label", label: "My Account" },
    {
      label: "Profile",
      icon: "i-lucide-user",
      onSelect: () => navigateTo("/profile"),
    },
    {
      label: "MFA",
      icon: "i-lucide-key-round",
      badge: user.isTwoFactorEnabled ? "Enabled" : "Disabled",
    },
    {
      label: "Log out",
      icon: "i-lucide-log-out",
      onSelect: onLogout,
    },
  ]
})

const displayName = computed(() => auth.user.value?.name || auth.user.value?.username || "Account")
const userInitials = computed(() => {
  const name = displayName.value
  if (!name || name === "Account") {
    return "?"
  }
  return userInitialsOf(name)
})
function userInitialsOf(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()
}

// Unused placeholder to keep toast binding referenced if future actions need it
void toast
void route
</script>

<template>
  <UDashboardSidebar
    collapsible="icon"
    :ui="{ footer: 'border-t border-default' }"
  >
    <!-- Workspace switcher -->
    <template #header>
      <UDropdownMenu
        v-if="activeWorkspace"
        :items="[
          workspaceOptions.map((workspace: Workspace) => ({
            label: workspace.name,
            icon: 'i-lucide-users',
            onSelect: () => onWorkspaceSelect(workspace),
          })),
          [
            {
              label: 'Add workspace',
              icon: 'i-lucide-plus',
              to: '/workspaces/new',
            },
          ],
        ]"
        :content="{ align: 'start' }"
        :ui="{ content: 'min-w-56' }"
      >
        <UButton
          variant="ghost"
          color="neutral"
          class="w-full justify-start"
          :ui="{ trailingIcon: 'text-dimmed' }"
        >
          <span class="flex aspect-square size-8 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-xs font-semibold text-primary">
            {{ workspaceInitials(activeWorkspace.name) }}
          </span>
          <span class="grid flex-1 text-left leading-tight">
            <span class="truncate font-medium">{{ activeWorkspace.name }}</span>
            <span class="truncate text-xs">{{ activeWorkspace.slug }}</span>
          </span>
          <UIcon
            name="i-lucide-chevrons-up-down"
            class="ml-auto shrink-0"
          />
        </UButton>
      </UDropdownMenu>
    </template>

    <!-- Main nav + workspace links -->
    <template #default>
      <UNavigationMenu
        orientation="vertical"
        :items="navItems"
        :ui="{ link: 'text-highlighted' }"
      />

      <USeparator v-if="workspaceLinks.length > 0" />

      <div
        v-if="workspaceLinks.length > 0"
        class="min-h-0 flex-1 overflow-y-auto"
      >
        <p class="px-2.5 py-1.5 text-xs font-medium text-dimmed">
          Workspaces
        </p>
        <UNavigationMenu
          orientation="vertical"
          :items="workspaceLinks"
          :ui="{ link: 'text-muted' }"
        />
      </div>
    </template>

    <!-- User menu -->
    <template #footer>
      <UDropdownMenu
        v-if="auth.user.value"
        :items="userItems as any"
        :content="{ align: 'end' }"
      >
        <UButton
          variant="ghost"
          color="neutral"
          class="w-full justify-start"
          :ui="{ trailingIcon: 'text-dimmed' }"
        >
          <UAvatar
            :src="auth.user.value.avatarUrl ?? undefined"
            :alt="displayName"
            :text="userInitials"
            size="xs"
          />
          <span class="grid flex-1 text-left leading-tight">
            <span class="truncate font-medium">{{ displayName }}</span>
            <span class="truncate text-xs">{{ auth.user.value.email }}</span>
          </span>
          <UIcon
            name="i-lucide-chevrons-up-down"
            class="ml-auto shrink-0"
          />
        </UButton>
      </UDropdownMenu>
    </template>
  </UDashboardSidebar>
</template>