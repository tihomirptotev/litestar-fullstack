<script setup lang="ts">
/**
 * About page — Nuxt port of the React app's `routes/_public/about.tsx`
 * (Konami-code easter egg, cursor-follow glow, features/workspace cards).
 * framer-motion animations are replaced with CSS transitions.
 * Layout: public layout's header/footer show for content pages — matching
 * React's _public pathless layout.
 */
definePageMeta({ layout: "public" })

useHead({ title: "About — Litestar Fullstack" })

// --- Konami code easter egg -----------------------------------------------
const KONAMI_CODE = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"]

const easterEggActive = ref(false)
const konamiIndex = ref(0)

const handleKeyDown = (event: KeyboardEvent) => {
  if (easterEggActive.value) {
    easterEggActive.value = false
    return
  }
  const expectedKey = KONAMI_CODE[konamiIndex.value]
  if (event.key === expectedKey) {
    konamiIndex.value += 1
    if (konamiIndex.value === KONAMI_CODE.length) {
      easterEggActive.value = true
      konamiIndex.value = 0
    }
  } else {
    konamiIndex.value = 0
  }
}

onMounted(() => window.addEventListener("keydown", handleKeyDown))
onBeforeUnmount(() => window.removeEventListener("keydown", handleKeyDown))

// --- Cursor-following glow -------------------------------------------------
const containerRef = ref<HTMLElement | null>(null)
const gradientX = ref(0)
const gradientY = ref(0)

const handleMouseMove = (event: MouseEvent) => {
  const rect = containerRef.value?.getBoundingClientRect()
  if (rect) {
    gradientX.value = ((event.clientX - rect.left) / Math.max(rect.width, 1)) * 100
    gradientY.value = ((event.clientY - rect.top) / Math.max(rect.height, 1)) * 100
  }
}

const glowStyle = computed(() => ({
  background: `radial-gradient(circle at ${gradientX.value}% ${gradientY.value}%, hsl(var(--primary) / 0.1), transparent 50%)`,
}))

// --- Content data ----------------------------------------------------------
const teamMembers = [
  { name: "Litestar Workspace", role: "Core Maintainers", avatar: "L" },
  { name: "Community", role: "Contributors", avatar: "C" },
  { name: "You", role: "Builder", avatar: "Y" },
]

const features = [
  { icon: "i-lucide-zap", title: "High Performance", description: "Built for speed with async-first architecture" },
  { icon: "i-lucide-star", title: "Type Safety", description: "End-to-end typing from Python to Vue" },
  { icon: "i-lucide-heart", title: "Developer Experience", description: "Intuitive APIs and excellent documentation" },
]
</script>

<template>
  <div
    ref="containerRef"
    role="presentation"
    class="relative min-h-screen"
    @mousemove="handleMouseMove"
  >
    <!-- Easter egg overlay -->
    <div
      v-if="easterEggActive"
      class="fixed inset-0 z-50 flex items-center justify-center bg-brand-navy"
      @click="easterEggActive = false"
    >
      <div class="relative">
        <!-- Orbiting particles -->
        <div
          v-for="i in 12"
          :key="`star-${i}`"
          class="easter-star absolute left-1/2 top-1/2 h-3 w-3 rounded-full bg-primary shadow-glow-sm"
          :style="{
            marginLeft: `${Math.cos((i / 12) * Math.PI * 2) * 150 - 6}px`,
            marginTop: `${Math.sin((i / 12) * Math.PI * 2) * 150 - 6}px`,
            animationDelay: `${i * 0.25}s`,
          }"
        />

        <!-- Central glowing logo -->
        <div class="easter-logo relative flex h-32 w-32 items-center justify-center rounded-full bg-primary/20 shadow-glow-lg backdrop-blur">
          <UIcon
            name="i-lucide-star"
            class="h-16 w-16 text-primary"
          />
        </div>

        <p class="easter-text absolute -bottom-20 left-1/2 -translate-x-1/2 whitespace-nowrap text-center text-lg font-semibold text-primary">
          You found the secret!
        </p>
      </div>

      <p class="absolute bottom-10 text-center text-sm text-muted-foreground">Press any key to exit</p>
    </div>

    <!-- Cursor-following glow effect -->
    <div
      class="pointer-events-none absolute inset-0"
      :style="glowStyle"
    />

    <PageContainer class="relative">
      <div class="mb-6">
        <UButton
          variant="ghost"
          color="neutral"
          size="sm"
          icon="i-lucide-arrow-left"
          to="/landing"
        >
          Back to home
        </UButton>
      </div>

      <PageHeader
        eyebrow="About"
        title="The Litestar Fullstack Project"
        description="A production-grade reference implementation for modern Python web applications."
      />

      <!-- Features grid -->
      <div class="mb-12 grid gap-6 md:grid-cols-3">
        <UCard
          v-for="feature in features"
          :key="feature.title"
          class="h-full backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 hover:shadow-lg"
          variant="subtle"
        >
          <div class="space-y-3 p-6">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary transition-transform duration-300 hover:rotate-5 hover:scale-110">
              <UIcon
                :name="feature.icon"
                class="h-6 w-6"
              />
            </div>
            <h3 class="text-lg font-semibold">
              {{ feature.title }}
            </h3>
            <p class="text-sm text-muted-foreground">
              {{ feature.description }}
            </p>
          </div>
        </UCard>
      </div>

      <!-- Workspace section -->
      <div class="mb-12">
        <h2 class="mb-6 text-2xl font-semibold">
          Built by the Community
        </h2>
        <div class="grid gap-6 md:grid-cols-3">
          <UCard
            v-for="(member, index) in teamMembers"
            :key="member.name"
            class="text-center backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 hover:shadow-lg"
            variant="subtle"
            :style="{ transitionDelay: `${index * 100}ms` }"
          >
            <div class="p-6">
              <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary">
                {{ member.avatar }}
              </div>
              <h3 class="font-semibold">
                {{ member.name }}
              </h3>
              <p class="text-sm text-muted-foreground">
                {{ member.role }}
              </p>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Links -->
      <div class="flex flex-wrap justify-center gap-4">
        <UButton
          variant="outline"
          color="neutral"
          icon="i-lucide-github"
          to="https://github.com/litestar-org"
          target="_blank"
        >
          GitHub
        </UButton>
        <UButton
          variant="outline"
          color="neutral"
          to="https://litestar.dev"
          target="_blank"
        >
          Documentation
        </UButton>
      </div>

      <!-- Hidden hint -->
      <p class="mt-16 text-center text-xs text-muted-foreground/40">
        Try the classic code...
      </p>
    </PageContainer>
  </div>
</template>

<style scoped>
.easter-star {
  animation: easter-star 3s ease-in-out infinite;
}
@keyframes easter-star {
  0% {
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1) rotate(180deg);
  }
  100% {
    opacity: 0;
    transform: scale(0) rotate(360deg);
  }
}

.easter-logo {
  animation: easter-logo 20s linear infinite;
}
@keyframes easter-logo {
  0% {
    transform: rotate(0deg) scale(1);
  }
  10%,
  30% {
    transform: rotate(72deg) scale(1.1);
  }
  20%,
  40% {
    transform: rotate(144deg) scale(1);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}

.easter-text {
  animation: easter-text 0.5s ease-out 0.5s both;
}
@keyframes easter-text {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>