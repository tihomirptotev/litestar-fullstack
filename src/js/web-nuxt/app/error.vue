<script setup lang="ts">
/**
 * Global error page — Nuxt port of the React app's `routes/$.tsx` 404
 * (splat route) + error boundary.
 */
import type { NuxtError } from "#app"

const props = defineProps<{
  error: NuxtError
}>()

const is404 = computed(() => props.error?.statusCode === 404)

const handleClearError = () => clearError({ redirect: "/" })
</script>

<template>
  <UApp>
    <div class="flex min-h-screen flex-col items-center justify-center gap-6 bg-background p-4 text-center">
      <p class="text-7xl font-bold tracking-tight text-primary sm:text-8xl">
        {{ error?.statusCode ?? 500 }}
      </p>
      <div class="space-y-2">
        <h1 class="text-2xl font-semibold tracking-tight">
          {{ is404 ? "Page not found" : "Something went wrong" }}
        </h1>
        <p class="max-w-md text-sm text-muted-foreground">
          {{
            is404
              ? "Sorry, we couldn't find the page you're looking for."
              : "An unexpected error occurred. Please try again."
          }}
        </p>
      </div>
      <div class="flex gap-3">
        <UButton
          @click="handleClearError"
        >
          Back to home
        </UButton>
      </div>
    </div>
  </UApp>
</template>