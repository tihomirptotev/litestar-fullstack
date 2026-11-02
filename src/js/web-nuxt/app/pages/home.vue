<script setup lang="ts">
/**
 * Home dashboard — Nuxt port of the React app's `routes/_app/home.tsx`.
 * Welcome header + your-workspaces card + quick-actions sidebar.
 */
import { listWorkspaces } from "#shared/api/sdk.gen"
import type { Workspace } from "#shared/api/types.gen"
import { useAuth } from "~/composables/useAuth"

definePageMeta({ layout: "app" })

const auth = useAuth()

const { data: workspacesData } = await useAsyncData<Workspace[]>("workspaces", async () => {
  const response = await listWorkspaces()
  return response.data?.items ?? []
})
const workspaces = computed(() => workspacesData.value ?? [])

const displayName = computed(() => auth.user.value?.name || auth.user.value?.email?.split("@")[0] || "there")

useHead({ title: "Home — Litestar Fullstack" })
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <PageHeader
        eyebrow="Dashboard"
        :title="`Welcome back, ${displayName}`"
        description="Manage your workspaces and explore the platform."
      >
        <template #actions>
          <UButton
            size="sm"
            icon="i-lucide-plus"
            to="/workspaces/new"
          >
            Create workspace
          </UButton>
        </template>
      </PageHeader>

      <div class="flex gap-6">
        <!-- Your Workspaces -->
        <UCard class="min-w-0 flex-1 transition-all hover:shadow-md">
          <template #header>
            <div class="space-y-1">
              <h2 class="text-lg font-semibold">Your Workspaces</h2>
              <p class="text-sm text-muted-foreground">Workspaces you're a member of</p>
            </div>
          </template>
          <div>
            <div
              v-if="workspaces.length > 0"
              class="space-y-2"
            >
              <NuxtLink
                v-for="workspace in workspaces.slice(0, 3)"
                :key="workspace.id"
                :to="`/workspaces/${workspace.id}`"
                class="flex items-center gap-2 rounded-lg border border-border/60 bg-background/60 p-3 transition-colors hover:bg-accent"
              >
                <UIcon
                  name="i-lucide-users"
                  class="h-4 w-4 text-muted-foreground"
                />
                <span class="font-medium">{{ workspace.name }}</span>
              </NuxtLink>
              <NuxtLink
                v-if="workspaces.length > 3"
                to="/workspaces"
                class="block text-center text-sm text-muted-foreground hover:text-foreground"
              >
                View all {{ workspaces.length }} workspaces
              </NuxtLink>
            </div>
            <div
              v-else
              class="py-4 text-center"
            >
              <p class="mb-3 text-sm text-muted-foreground">You're not a member of any workspaces yet.</p>
              <UButton
                size="sm"
                variant="outline"
                color="neutral"
                to="/workspaces/new"
              >
                Create your first workspace
              </UButton>
            </div>
          </div>
        </UCard>

        <!-- Quick Actions -->
        <UCard class="h-fit w-72 shrink-0 border-border/40 bg-linear-to-br from-muted/30 to-muted/10 max-md:hidden">
          <template #header>
            <div class="space-y-1">
              <h2 class="text-lg font-semibold">Quick Actions</h2>
              <p class="text-sm text-muted-foreground">Common tasks</p>
            </div>
          </template>
          <div class="space-y-1.5">
            <NuxtLink
              v-for="action in [
                { to: '/workspaces/new', icon: 'i-lucide-plus', iconClass: 'bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground', title: 'Create a new workspace', desc: 'Start collaborating' },
                { to: '/profile', icon: 'i-lucide-settings', iconClass: 'bg-orange-500/10 text-orange-600 dark:text-orange-400 group-hover:bg-orange-500 group-hover:text-white', title: 'Edit your profile', desc: 'Manage account settings' },
                { to: '/workspaces', icon: 'i-lucide-users', iconClass: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 group-hover:bg-blue-500 group-hover:text-white', title: 'Browse all workspaces', desc: 'View your workspaces' },
              ]"
              :key="action.to"
              :to="action.to"
              class="group flex items-center gap-3 rounded-lg bg-background/60 p-3 transition-all hover:bg-background hover:shadow-sm"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors" :class="action.iconClass">
                <UIcon
                  :name="action.icon"
                  class="h-4 w-4"
                />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium">{{ action.title }}</p>
                <p class="text-xs text-muted-foreground">{{ action.desc }}</p>
              </div>
              <UIcon
                name="i-lucide-chevron-right"
                class="h-4 w-4 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5 group-hover:text-foreground"
              />
            </NuxtLink>
          </div>
        </UCard>
      </div>
    </PageContainer>
  </div>
</template>