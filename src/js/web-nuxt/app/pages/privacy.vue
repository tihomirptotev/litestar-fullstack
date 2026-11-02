<script setup lang="ts">
/**
 * Privacy policy — Nuxt port of the React app's `routes/_public/privacy.tsx`.
 */
definePageMeta({ layout: false })

useHead({ title: "Privacy Policy — Litestar Fullstack" })
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <AuthHeroPanel
      :show-testimonial="false"
      description="Your privacy matters. Learn how we handle your data."
    />

    <div class="flex flex-1 flex-col items-center justify-center bg-brand-gray-light px-4 py-12 dark:bg-background">
      <div class="w-full max-w-xl space-y-6">
        <div class="space-y-2">
          <p class="text-xs uppercase tracking-[0.2em] text-secondary-foreground/80">Legal</p>
          <h1 class="text-3xl font-semibold tracking-tight">
            Privacy Policy
          </h1>
          <p class="text-muted-foreground">How we collect, store, and use data inside the Litestar reference app.</p>
        </div>

        <div class="space-y-6 text-muted-foreground">
          <p>
            We collect only the information required to operate this reference application, including account details and security events needed to keep the platform reliable.
          </p>
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-foreground">Data collected</h3>
            <p>Account profile data, authentication events, team membership metadata, and operational diagnostics for queues and background jobs.</p>
          </div>
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-foreground">Retention</h3>
            <p>Logs and operational data are retained for a limited period and deleted automatically unless required for security investigations.</p>
          </div>
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-foreground">Third parties</h3>
            <p>We rely on infrastructure providers for hosting, email delivery, and monitoring. Data is shared only as necessary to provide service.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>