<script setup lang="ts">
/**
 * Index — Nuxt port of the React app's `routes/index.tsx`: authenticated
 * visitors land on /home, everyone else on the marketing page.
 *
 * The redirect decision runs as inline route middleware instead of top-level
 * `await` in setup: awaited logic in `<script setup>` suspends the whole app
 * behind a blank `<div />` while the profile request resolves (and nothing
 * renders until the follow-up navigation completes). Route middleware gets
 * the same "decide before first paint" behavior without suspending the app —
 * if the promise rejects or hangs, the splash chrome from layouts still
 * renders, and returning `navigateTo` here skips rendering this page
 * entirely.
 */
definePageMeta({
  middleware: [
    async () => {
      const auth = useAuth()

      await auth.checkAuth()

      return navigateTo(auth.isAuthenticated.value ? "/home" : "/landing", { replace: true })
    },
  ],
})
</script>

<template>
  <div />
</template>