<script setup lang="ts">
/**
 * Public layout — Nuxt port of the React app's `layouts/public-layout.tsx`.
 * Landing and auth pages render bare (they handle their own chrome);
 * content pages (about/privacy/terms) get a simple header/footer.
 * Dark mode is handled globally via Nuxt UI's color mode — no toggle here.
 */
const route = useRoute()
const path = computed(() => route.path)

const isLandingPage = computed(() => path.value === "/" || path.value === "/landing")
const isAuthPage = computed(
  () =>
    path.value === "/login" ||
    path.value === "/signup" ||
    path.value === "/forgot-password" ||
    path.value.startsWith("/reset-password") ||
    path.value === "/mfa-challenge" ||
    path.value === "/verify-email" ||
    path.value.startsWith("/auth/"),
)
const showHeaderFooter = computed(() => !isLandingPage.value && !isAuthPage.value)
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <!-- Header for content pages (terms, privacy, about) -->
    <header
      v-if="showHeaderFooter"
      class="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur"
    >
      <div class="container mx-auto flex h-14 items-center justify-between px-4">
        <NuxtLink
          to="/"
          class="flex items-center gap-2 text-foreground transition-opacity hover:opacity-80"
        >
          <div class="h-7 w-7 rounded-lg bg-primary/20" />
          <span class="font-semibold">Litestar Fullstack</span>
        </NuxtLink>
        <div class="flex items-center gap-3">
          <UButton
            variant="ghost"
            size="sm"
            to="/login"
          >
            Log in
          </UButton>
          <UButton
            size="sm"
            to="/signup"
          >
            Sign up
          </UButton>
        </div>
      </div>
    </header>

    <main class="flex flex-1">
      <slot />
    </main>

    <!-- Footer for content pages (terms, privacy, about) -->
    <footer
      v-if="showHeaderFooter"
      class="border-t border-border/60 bg-background/80"
    >
      <div class="container mx-auto px-4 py-6">
        <div class="flex flex-wrap items-center justify-between gap-4 text-sm text-muted-foreground">
          <div class="flex items-center gap-2">
            <div class="h-6 w-6 rounded-md bg-primary/20" />
            <span class="font-medium text-foreground">Litestar Fullstack</span>
          </div>
          <div class="flex gap-6">
            <NuxtLink
              to="/privacy"
              class="transition-colors hover:text-foreground"
            >
              Privacy
            </NuxtLink>
            <NuxtLink
              to="/terms"
              class="transition-colors hover:text-foreground"
            >
              Terms
            </NuxtLink>
            <NuxtLink
              to="/about"
              class="transition-colors hover:text-foreground"
            >
              About
            </NuxtLink>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>