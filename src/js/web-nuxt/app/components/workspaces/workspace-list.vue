<script setup lang="ts">
/**
 * WorkspaceList — Nuxt port of the React app's `components/workspaces/workspace-list.tsx`.
 * Lists the user's workspaces as selectable cards; current workspace is highlighted and
 * clicking an avatar switches it in the auth store.
 */
import { computed, ref, watch } from "vue"
import { listWorkspaces, type Workspace } from "#shared/api/sdk.gen"
import { useAuth } from "~/composables/useAuth"

const auth = useAuth()
const search = ref("")

const {
  data: workspacesData,
  error: workspacesError,
  status,
} = useAsyncData<Workspace[]>(
  "workspaces",
  async () => {
    const response = await listWorkspaces()
    return response.data?.items ?? []
  },
  { default: () => [] },
)

const isLoading = computed(() => status.value === "pending")
const isError = computed(() => Boolean(workspacesError.value))

watch(
  workspacesData,
  (workspaces) => {
    if (!isLoading.value && !isError.value && workspaces.length) {
      auth.setWorkspaces(workspaces)
    }
  },
  { immediate: true },
)

const filteredWorkspaces = computed(() =>
  workspacesData.value.filter((workspace) => workspace.name.toLowerCase().includes(search.value.toLowerCase()) || workspace.description?.toLowerCase().includes(search.value.toLowerCase())),
)

function getWorkspaceInitials(name: string): string {
  return name
    .split(/\s+/)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

function getWorkspaceColor(name: string): string {
  const colors = [
    "bg-blue-500/15 text-blue-600 dark:text-blue-400",
    "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
    "bg-violet-500/15 text-violet-600 dark:text-violet-400",
    "bg-amber-500/15 text-amber-600 dark:text-amber-400",
    "bg-rose-500/15 text-rose-600 dark:text-rose-400",
    "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400",
    "bg-fuchsia-500/15 text-fuchsia-600 dark:text-fuchsia-400",
    "bg-orange-500/15 text-orange-600 dark:text-orange-400",
  ]
  const index = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  return colors[index]
}
</script>

<template>
  <div>
    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center py-16"
    >
      <div class="flex flex-col items-center gap-3">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <p class="text-sm text-muted-foreground">Loading workspaces…</p>
      </div>
    </div>

    <!-- Error state -->
    <UCard
      v-else-if="isError"
      class="border-dashed border-error/30 bg-error/5"
    >
      <p class="py-12 text-center text-muted-foreground">We couldn't load workspaces yet. Try refreshing.</p>
    </UCard>

    <!-- Empty state -->
    <UCard
      v-else-if="workspacesData.length === 0"
      class="border-dashed border-2"
    >
      <div class="space-y-6 py-16 text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <UIcon
            name="i-lucide-users"
            class="h-8 w-8 text-primary"
          />
        </div>
        <div class="space-y-2">
          <h3 class="text-lg font-semibold">Create your first workspace</h3>
          <p class="mx-auto max-w-md text-sm text-muted-foreground">
            Workspaces help you organize members and control access across the app. Get started by creating your first workspace.
          </p>
        </div>
        <UButton
          size="lg"
          to="/workspaces/new"
          icon="i-lucide-plus"
        >
          Create workspace
        </UButton>
      </div>
    </UCard>

    <!-- Workspace grid -->
    <div
      v-else
      class="space-y-6"
    >
      <div
        v-if="workspacesData.length > 3"
        class="relative max-w-md"
      >
        <UIcon
          name="i-lucide-search"
          class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
        />
        <UInput
          v-model="search"
          placeholder="Search workspaces..."
          class="pl-10"
        />
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <UCard
          v-for="workspace in filteredWorkspaces"
          :key="workspace.id"
          class="group relative overflow-hidden transition-all hover:shadow-md"
          :class="auth.currentWorkspace.value?.id === workspace.id ? 'border-primary/50 bg-primary/5 shadow-primary/10 shadow-sm ring-1 ring-primary/20' : 'border-border/60 hover:border-border'"
          variant="subtle"
        >
          <!-- Active indicator stripe -->
          <div
            v-if="auth.currentWorkspace.value?.id === workspace.id"
            class="absolute inset-y-0 left-0 w-1 bg-primary"
          />

          <div class="pb-3">
            <div class="flex items-start gap-3">
              <button
                type="button"
                class="group/avatar relative"
                :title="auth.currentWorkspace.value?.id === workspace.id ? 'Current workspace' : 'Click to switch to this workspace'"
                @click="auth.setCurrentWorkspace(workspace)"
              >
                <span
                  class="flex h-12 w-12 items-center justify-center rounded-full text-sm font-semibold transition-all"
                  :class="[getWorkspaceColor(workspace.name), auth.currentWorkspace.value?.id !== workspace.id && 'group-hover/avatar:ring-2 group-hover/avatar:ring-primary/30']"
                >
                  {{ getWorkspaceInitials(workspace.name) }}
                </span>
                <span
                  v-if="auth.currentWorkspace.value?.id === workspace.id"
                  class="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-primary-foreground ring-2 ring-background"
                >
                  <UIcon
                    name="i-lucide-check"
                    class="h-3 w-3"
                  />
                </span>
              </button>

              <div class="min-w-0 flex-1">
                <NuxtLink
                  :to="`/workspaces/${workspace.id}`"
                  class="truncate font-semibold text-foreground hover:underline"
                >
                  {{ workspace.name }}
                </NuxtLink>
                <div class="mt-1 flex items-center gap-2">
                  <span class="flex items-center gap-1 text-xs text-muted-foreground">
                    <UIcon
                      name="i-lucide-users"
                      class="h-3 w-3"
                    />
                    {{ workspace.members?.length ?? 0 }} member{{ (workspace.members?.length ?? 0) !== 1 ? "s" : "" }}
                  </span>
                  <UBadge
                    v-if="workspace.members?.find((m) => m.userId === auth.user.value?.id)?.isOwner"
                    variant="outline"
                    class="h-5 px-1.5 text-[10px] font-medium"
                  >
                    Owner
                  </UBadge>
                  <UBadge
                    v-else-if="workspace.members?.find((m) => m.userId === auth.user.value?.id)?.role === 'ADMIN'"
                    variant="outline"
                    icon="i-lucide-shield"
                    class="h-5 px-1.5 text-[10px] font-medium"
                  >
                    Admin
                  </UBadge>
                </div>
              </div>
            </div>
          </div>

          <div class="pt-0">
            <p
              v-if="workspace.description"
              class="line-clamp-2 min-h-10 text-sm text-muted-foreground"
            >
              {{ workspace.description }}
            </p>
            <p
              v-else
              class="min-h-10 text-sm italic text-muted-foreground/60"
            >
              No description
            </p>

            <div
              v-if="(workspace.tags ?? []).length > 0"
              class="mt-3 flex flex-wrap gap-1.5"
            >
              <UBadge
                v-for="tag in (workspace.tags ?? []).slice(0, 3)"
                :key="tag.id"
                variant="secondary"
                class="px-2 py-0.5 text-[10px]"
              >
                {{ tag.name }}
              </UBadge>
              <UBadge
                v-if="(workspace.tags ?? []).length > 3"
                variant="outline"
                class="px-2 py-0.5 text-[10px]"
              >
                +{{ (workspace.tags ?? []).length - 3 }}
              </UBadge>
            </div>

            <div class="mt-4 border-t border-border/60 pt-3">
              <NuxtLink
                :to="`/workspaces/${workspace.id}`"
                class="group/link flex items-center justify-between text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                <span>View workspace</span>
                <UIcon
                  name="i-lucide-chevron-right"
                  class="h-4 w-4 transition-transform group-hover/link:translate-x-0.5"
                />
              </NuxtLink>
            </div>
          </div>
        </UCard>
      </div>

      <UCard
        v-if="filteredWorkspaces.length === 0 && search"
        class="border-dashed"
      >
        <p class="py-12 text-center text-muted-foreground">No workspaces match "{{ search }}"</p>
      </UCard>

      <p
        v-if="filteredWorkspaces.length > 0"
        class="text-center text-xs text-muted-foreground"
      >
        Showing {{ filteredWorkspaces.length }} of {{ workspacesData.length }} workspace{{ workspacesData.length === 1 ? "" : "s" }}
      </p>
    </div>
  </div>
</template>