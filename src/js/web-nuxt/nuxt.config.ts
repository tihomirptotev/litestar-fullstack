// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/ui"],

  devtools: {
    enabled: true,
  },

  css: ["~/assets/css/main.css"],

  // SPA mode to match the current React app's behavior
  // (bearer token in localStorage, backend serves the built SPA).
  // Revisit for hybrid/SSR once auth moves to httpOnly cookies.
  ssr: false,

  nitro: {
    devProxy: {
      // Proxy API calls to the Litestar backend during development.
      "/api": {
        target: process.env.LITESTAR_URL ?? "http://127.0.0.1:8000",
        changeOrigin: true,
        prependPath: true,
      },
    },
  },

  // Route rules only affect pre-rendering in SPA mode; everything is client-rendered.
  routeRules: {
    "/**": { ssr: false },
  },

  runtimeConfig: {
    public: {
      // Base URL of the Litestar API (empty string = same origin, matching
      // the React app's VITE_API_URL behavior).
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? "",
    },
  },

  compatibilityDate: "2026-06-30",
})
