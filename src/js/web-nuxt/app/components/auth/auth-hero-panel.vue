<script setup lang="ts">
/**
 * Auth hero panel — Nuxt port of the React app's
 * `components/auth/auth-hero-panel.tsx`.
 * Tech-stack badges are rendered from simple inline SVG data instead of the
 * React `Icons.python/react/vite/typescript` components.
 */
const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    showTestimonial?: boolean
  }>(),
  {
    title: "Litestar Fullstack",
    description: "A modern, high-performance Python web framework with Vue, Vite, and Nuxt UI.",
    showTestimonial: true,
  },
)
</script>

<template>
  <div class="relative hidden min-h-screen w-1/2 max-w-2xl flex-col bg-brand-navy p-10 text-white lg:flex">
    <RetroGrid />

    <NuxtLink
      to="/"
      class="relative z-20"
    >
      <div class="flex items-center text-lg font-medium">
        <IconsLogo class="mr-2 h-6 w-6" />
        {{ title }}
      </div>
    </NuxtLink>

    <div class="relative z-20 mt-auto">
      <div
        v-if="showTestimonial"
        class="space-y-4"
      >
        <p class="text-lg font-medium leading-relaxed">
          {{ description }}
        </p>
        <div class="flex items-center gap-4">
          <div class="flex -space-x-1">
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechPython class="h-5 w-5" />
            </div>
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 ring-2 ring-brand-navy backdrop-blur-sm">
              <IconsTechReact class="h-5 w-5" />
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
      <p
        v-else
        class="text-lg font-medium leading-relaxed text-white/70"
      >
        {{ description }}
      </p>
    </div>
  </div>
</template>