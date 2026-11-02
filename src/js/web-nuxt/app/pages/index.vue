<script setup lang="ts">
/**
 * Index — Nuxt port of the React app's `routes/index.tsx`: authenticated
 * visitors land on /home, everyone else on the marketing page.
 */
const auth = useAuth()

// checkAuth only runs in app middleware/definePageMeta-protected pages; here we
// mirror the React app's persisted-state fast path.
await auth.checkAuth()

if (auth.isAuthenticated.value) {
  await navigateTo("/home", { replace: true })
} else {
  await navigateTo("/landing", { replace: true })
}
</script>

<template>
  <div />
</template>