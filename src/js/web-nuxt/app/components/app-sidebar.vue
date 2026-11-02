<script setup lang="ts">
/**
 * App sidebar — Nuxt port of the React app's `app-sidebar.tsx`,
 * `nav-main.tsx`, `nav-projects.tsx`, `team-switcher.tsx` and `nav-user.tsx`
 * collapsed into one component using Nuxt UI's `UDashboardSidebar`.
 */
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui"
import { getAccessToken } from "#shared/api/config"
import { listTeams } from "#shared/api/sdk.gen"
import type { Team, User } from "#shared/api/types.gen"
import { unwrapAs } from "~/composables/api"

const auth = useAuth()
const route = useRoute()
const toast = useToast()

// --- Teams fetch + store sync (mirrors the React useQuery + useEffect sync) ---
const teamsData = ref<Team[]>([])
const teamsLoading = ref(false)

const loadTeams = async () => {
  if (!getAccessToken() && !auth.isAuthenticated.value) {
    return
  }
  teamsLoading.value = true
  try {
    const data = await unwrapAs<unknown, unknown, { items?: Team[] }>(listTeams())
    teamsData.value = data.items ?? []
    auth.setTeams(teamsData.value)
  } catch {
    // Non-fatal — sidebar falls back to the store's team list.
  } finally {
    teamsLoading.value = false
  }
}

onMounted(() => {
  loadTeams()
})

watch(
  () => auth.isAuthenticated.value,
  (authenticated) => {
    if (authenticated) {
      loadTeams()
    }
  },
)

// Keep local list in sync when teams change elsewhere (e.g. create team page).
watch(
  () => auth.teams.value.map((team: Team) => team.id).join("|"),
  (storeIds) => {
    const localIds = teamsData.value.map((team) => team.id).join("|")
    if (storeIds !== localIds) {
      teamsData.value = auth.teams.value
    }
  },
)

const teamOptions = computed<Team[]>(() => (teamsData.value.length > 0 ? teamsData.value : auth.teams.value))

// --- Navigation items ---
const navItems = computed<NavigationMenuItem[]>(() => {
  const items: NavigationMenuItem[] = [
    {
      label: "Home",
      icon: "i-lucide-house",
      to: "/home",
    },
    {
      label: "Teams",
      icon: "i-lucide-users",
      to: "/teams",
      children: [
        { label: "All teams", to: "/teams" },
        { label: "Create new", to: "/teams/new" },
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

const teamLinks = computed<NavigationMenuItem[]>(() =>
  teamOptions.value.map((team: Team) => ({
    label: team.name,
    icon: "i-lucide-users",
    to: `/teams/${team.id}`,
  })),
)

// --- Team switcher ---
const activeTeam = computed<Team | null>(() => {
  const { currentTeam } = auth
  if (currentTeam.value) {
    return teamOptions.value.find((team) => team.id === currentTeam.value?.id) ?? teamOptions.value[0] ?? null
  }
  return teamOptions.value[0] ?? null
})

const teamInitials = (name: string) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

const onTeamSelect = (team: Team) => {
  auth.setCurrentTeam(team)
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
    <!-- Team switcher -->
    <template #header>
      <UDropdownMenu
        v-if="activeTeam"
        :items="[
          teamOptions.map((team: Team) => ({
            label: team.name,
            icon: 'i-lucide-users',
            onSelect: () => onTeamSelect(team),
          })),
          [
            {
              label: 'Add team',
              icon: 'i-lucide-plus',
              to: '/teams/new',
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
            {{ teamInitials(activeTeam.name) }}
          </span>
          <span class="grid flex-1 text-left leading-tight">
            <span class="truncate font-medium">{{ activeTeam.name }}</span>
            <span class="truncate text-xs">{{ activeTeam.slug }}</span>
          </span>
          <UIcon
            name="i-lucide-chevrons-up-down"
            class="ml-auto shrink-0"
          />
        </UButton>
      </UDropdownMenu>
    </template>

    <!-- Main nav + team links -->
    <template #default>
      <UNavigationMenu
        orientation="vertical"
        :items="navItems"
        :ui="{ link: 'text-highlighted' }"
      />

      <USeparator v-if="teamLinks.length > 0" />

      <div
        v-if="teamLinks.length > 0"
        class="min-h-0 flex-1 overflow-y-auto"
      >
        <p class="px-2.5 py-1.5 text-xs font-medium text-dimmed">
          Teams
        </p>
        <UNavigationMenu
          orientation="vertical"
          :items="teamLinks"
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