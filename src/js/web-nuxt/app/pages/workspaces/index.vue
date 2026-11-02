<script setup lang="ts">
/**
 * Workspaces list page — Nuxt port of the React app's `routes/_app/workspaces/index.tsx`.
 */
definePageMeta({ layout: "app" })

useHead({ title: "Workspaces — Litestar Fullstack" })
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <PageHeader
        eyebrow="Workspace"
        title="Workspaces"
        description="Manage your workspaces and collaborate with members."
      >
        <template #actions>
          <UButton
            size="sm"
            to="/workspaces/new"
            icon="i-lucide-plus"
          >
            New workspace
          </UButton>
        </template>
      </PageHeader>

      <WorkspacesWorkspaceList />
    </PageContainer>
  </div>
</template>