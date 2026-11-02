<script setup lang="ts">
/**
 * Login page — Nuxt port of the React app's `routes/_public/login.tsx` +
 * `components/auth/auth-form.tsx` (login branch).
 */

import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import UserLoginForm from "~/components/auth/user-login-form.vue"
import { validateRedirectUrl } from "~/utils/redirect-utils"

definePageMeta({ layout: false })

useHead({ title: "Sign in — Litestar Fullstack" })

const route = useRoute()

const redirectParam = computed(() => (route.query.redirect as string | undefined) || null)
const validatedRedirect = computed(() => validateRedirectUrl(redirectParam.value))

const toggleQuery = computed(() => (validatedRedirect.value ? { redirect: validatedRedirect.value } : {}))

defineExpose({})
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <!-- Left panel with RetroGrid - hidden on mobile -->
    <AuthHeroPanel
      title="Litestar Fullstack"
      description="Build high-performance web applications with Python and Vue. Seamless SPA experience powered by Nuxt."
    />

    <!-- Right panel with form - centers on mobile when hero is hidden -->
    <div class="flex flex-1 flex-col items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
      <UButton
        variant="ghost"
        color="neutral"
        class="absolute right-4 top-4 md:right-8 md:top-8"
        to="/signup"
        :query="toggleQuery"
      >
        Need an account?
      </UButton>

      <div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div class="flex flex-col space-y-2 text-center">
          <h1 class="flex items-center justify-center gap-2 text-2xl font-semibold tracking-tight">
            <IconsSparkle class="h-5 w-5" />
            Welcome back
          </h1>
          <p class="text-sm text-muted-foreground">
            Enter your credentials to sign in to your account
          </p>
        </div>

        <UserLoginForm :redirect-url="validatedRedirect" />

        <div class="text-center">
          <NuxtLink
            to="/forgot-password"
            class="text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
          >
            Forgot your password?
          </NuxtLink>
        </div>

        <p class="px-8 text-center text-sm text-muted-foreground">
          By continuing, you agree to our
          <NuxtLink
            to="/terms"
            class="underline underline-offset-4 hover:text-primary"
          >
            Terms of Service
          </NuxtLink>
          and
          <NuxtLink
            to="/privacy"
            class="underline underline-offset-4 hover:text-primary"
          >
            Privacy Policy
          </NuxtLink>
          .
        </p>
      </div>
    </div>
  </div>
</template>