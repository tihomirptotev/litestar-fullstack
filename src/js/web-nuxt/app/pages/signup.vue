<script setup lang="ts">
/**
 * Signup page — Nuxt port of the React app's `routes/_public/signup.tsx`
 * (AuthForm signup branch).
 */

import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import UserSignupForm from "~/components/auth/user-signup-form.vue"
import { validateRedirectUrl } from "~/utils/redirect-utils"

definePageMeta({ layout: false })

useHead({ title: "Create account — Litestar Fullstack" })

const route = useRoute()

const redirectParam = computed(() => (route.query.redirect as string | undefined) || null)
const validatedRedirect = computed(() => validateRedirectUrl(redirectParam.value))

const toggleQuery = computed(() => (validatedRedirect.value ? { redirect: validatedRedirect.value } : {}))
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
        to="/login"
        :query="toggleQuery"
      >
        Sign in
      </UButton>

      <div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div class="flex flex-col space-y-2 text-center">
          <h1 class="flex items-center justify-center gap-2 text-2xl font-semibold tracking-tight">
            <IconsSparkle class="h-5 w-5" />
            Create account
          </h1>
          <p class="text-sm text-muted-foreground">
            Enter your details to create your account
          </p>
        </div>

        <UserSignupForm :redirect-url="validatedRedirect" />

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