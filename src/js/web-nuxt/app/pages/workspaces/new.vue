<script setup lang="ts">
/**
 * New workspace page — Nuxt port of the React app's `routes/_app/workspaces/new.tsx`.
 */
definePageMeta({ layout: "app" })

useHead({ title: "Create New Workspace — Litestar Fullstack" })

const tips = [
  { icon: "i-lucide-users", title: "Collaborate together", description: "Group members and share resources" },
  { icon: "i-lucide-shield", title: "Role-based access", description: "Control what members can do" },
  { icon: "i-lucide-user-plus", title: "Invite members", description: "Add people by email" },
  { icon: "i-lucide-tag", title: "Organize with tags", description: "Categorize for easy discovery" },
]
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <PageHeader
        eyebrow="Workspaces"
        title="Create New Workspace"
        description="Set up a new workspace to organize members and manage access."
      />

      <div class="flex gap-6">
        <!-- Main form -->
        <UCard class="min-w-0 flex-1">
          <template #header>
            <h2 class="text-lg font-semibold">Workspace Details</h2>
          </template>
          <WorkspacesCreateWorkspaceForm />
        </UCard>

        <!-- Sidebar tips - styled like Quick Actions -->
        <UCard
          class="h-fit w-72 shrink-0 border-border/40 bg-linear-to-br from-muted/30 to-muted/10 max-md:hidden"
        >
          <template #header>
            <div class="space-y-1">
              <h2 class="text-lg font-semibold">Getting Started</h2>
              <p class="text-sm text-muted-foreground">Tips for your new workspace</p>
            </div>
          </template>
          <div class="space-y-1.5">
            <div
              v-for="tip in tips"
              :key="tip.title"
              class="group flex items-center gap-3 rounded-lg bg-background/60 p-3"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <UIcon
                  :name="tip.icon"
                  class="h-4 w-4"
                />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium">{{ tip.title }}</p>
                <p class="text-xs text-muted-foreground">{{ tip.description }}</p>
              </div>
              <UIcon
                name="i-lucide-chevron-right"
                class="h-4 w-4 text-muted-foreground/30"
              />
            </div>
          </div>
        </UCard>
      </div>
    </PageContainer>
  </div>
</template>