import { defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  input: "./shared/openapi.json",
  output: {
    path: "./shared/api",
    format: "biome",
  },
  plugins: [
    "@hey-api/typescript",
    "@hey-api/schemas",
    {
      name: "@hey-api/sdk",
      asClass: false,
      // Flat named functions (e.g. accountLogin), matching the React app's
      // generated SDK style.
      operationId: true,
      throwOnError: false,
    },
    // NOTE: intentionally NO @tanstack/[vue-]query plugin — data fetching goes
    // through Nuxt's useFetch/useAsyncData composables (app/composables/api.ts).
  ],
})