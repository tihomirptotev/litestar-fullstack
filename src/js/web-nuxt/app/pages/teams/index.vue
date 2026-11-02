<script setup lang="ts">
/**
 * Teams list page — Nuxt port of the React app's `routes/_app/teams/index.tsx`.
 */
definePageMeta({ layout: "app" })

useHead({ title: "Teams — Litestar Fullstack" })
</script>

<template>
  <div class="flex-1 space-y-8">
    <PageContainer>
      <PageHeader
        eyebrow="Workspace"
        title="Teams"
        description="Manage your teams and collaborate with members."
      >
        <template #actions>
          <UButton
            size="sm"
            to="/teams/new"
            icon="i-lucide-plus"
          >
            New team
          </UButton>
        </template>
      </PageHeader>

      <TeamsTeamList />
    </PageContainer>
  </div>
</template>