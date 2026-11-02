<script setup lang="ts">
/**
 * Landing page — Nuxt port of the React app's
 * `components/landing/landing-page.tsx`.
 * Left RetroGrid hero panel + centered brand content; theme toggle handled by
 * Nuxt UI's global color mode (mode: "system"), no per-page toggle needed.
 */
definePageMeta({ layout: false })

useHead({ title: "Litestar Fullstack" })

const year = new Date().getFullYear()
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <!-- Left panel with RetroGrid - hidden on mobile -->
    <div class="relative hidden min-h-screen w-1/2 max-w-2xl flex-col bg-brand-navy p-10 text-white lg:flex">
      <RetroGrid />

      <NuxtLink
        to="/"
        class="relative z-20"
      >
        <div class="flex items-center text-lg font-medium">
          <IconsLogo class="mr-2 h-6 w-6" />
          Litestar Fullstack
        </div>
      </NuxtLink>

      <div class="relative z-20 mt-auto">
        <p class="text-lg font-medium leading-relaxed">Build high-performance web applications with Python and Vue. Seamless SPA experience powered by Nuxt.</p>

        <div class="mt-4 flex items-center gap-4">
          <div class="flex -space-x-1">
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechPython class="h-5 w-5" />
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechReact class="h-5 w-5 text-[#61DAFB]" />
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechVite class="h-5 w-5" />
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechTypescript class="h-5 w-5" />
            </div>
          </div>
          <div class="text-sm text-white/70">
            <span class="font-medium text-white">Built with</span> Python, Vue & modern tooling
          </div>
        </div>
      </div>
    </div>

    <!-- Right panel with content -->
    <div class="flex flex-1 flex-col bg-brand-gray-light dark:bg-background">
      <!-- Header with sign in -->
      <div class="flex items-center justify-end gap-2 p-4 md:p-8">
        <UButton
          variant="ghost"
          color="neutral"
          to="/login"
        >
          Sign in
        </UButton>
      </div>

      <!-- Main content - centered -->
      <main class="flex flex-1 flex-col items-center justify-center px-4 pb-16">
        <IconsLogoBrand class="h-16 w-16" />

        <h1 class="mt-8 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Litestar Fullstack
        </h1>

        <p class="mt-4 max-w-md text-center text-lg text-muted-foreground">A production-ready Python + Vue reference application</p>

        <div class="mt-10 flex gap-4">
          <UButton
            size="lg"
            to="/signup"
          >
            Try the demo
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="lg"
            trailing-icon="i-lucide-arrow-right"
            to="https://github.com/litestar-org/litestar-fullstack"
            target="_blank"
          >
            View source
          </UButton>
        </div>
      </main>

      <!-- Footer -->
      <footer class="py-6 text-center text-sm text-muted-foreground">© {{ year }} Litestar Organization · MIT License</footer>
    </div>
  </div>
</template>