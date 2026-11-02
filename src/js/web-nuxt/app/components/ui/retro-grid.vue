<script lang="ts" setup>
/**
 * RetroGrid decorative background — Nuxt port of the React app's
 * `components/ui/retro-grid.tsx` (pure CSS animation, no framer-motion).
 */
withDefaults(
  defineProps<{
    angle?: number
    cellSize?: number
    opacity?: number
    gridLineColor?: string
    gridLineStrongColor?: string
  }>(),
  {
    angle: 65,
    cellSize: 60,
    opacity: 0.6,
    gridLineColor: "rgba(255,255,255,0.06)",
    gridLineStrongColor: "rgba(255,255,255,0.12)",
  },
)
</script>

<template>
  <div
    class="pointer-events-none absolute inset-0 overflow-hidden select-none"
    :style="{ opacity, perspective: '200px' }"
    aria-hidden="true"
  >
    <!-- Stars -->
    <div
      class="absolute inset-0 animate-[star-drift_22s_linear_infinite]"
      :style="{
        backgroundImage:
          'radial-gradient(circle at center, var(--grid-star) 0%, transparent 100%)',
        backgroundSize: '80px 80px',
        opacity: 0.5,
      }"
    />

    <!-- Rotated grid layers -->
    <div
      class="absolute inset-0 flex items-center justify-center"
      :style="{
        transform: `rotateX(${angle}deg) scaleZ(1.4)`,
        transformOrigin: '100% 0%',
      }"
    >
      <div
        class="absolute inset-0 animate-[grid_15s_linear_infinite] [background-size:60px_60px] [height:600vw] [width:600vw] opacity-40"
        :style="{
          backgroundImage: `linear-gradient(to right, ${gridLineStrongColor} 1px, transparent 0), linear-gradient(to bottom, ${gridLineStrongColor} 1px, transparent 0)`,
          backgroundSize: `${cellSize}px ${cellSize}px`,
        }"
      />
      <div
        class="absolute inset-0 animate-[grid_20s_linear_infinite] [background-size:90px_90px] [height:600vw] [width:600vw] opacity-40"
        :style="{
          backgroundImage: `linear-gradient(to right, ${gridLineColor} 1px, transparent 0), linear-gradient(to bottom, ${gridLineColor} 1px, transparent 0)`,
          backgroundSize: `${cellSize}px ${cellSize}px`,
        }"
      />
    </div>

    <!-- Horizon glow -->
    <div
      class="absolute inset-x-0 bottom-0 h-64"
      :style="{
        backgroundImage:
          'radial-gradient(ellipse 80% 50% at 50% -20%, var(--grid-glow), transparent 70%)',
      }"
    />

    <!-- Fade to page background -->
    <div class="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
  </div>
</template>
