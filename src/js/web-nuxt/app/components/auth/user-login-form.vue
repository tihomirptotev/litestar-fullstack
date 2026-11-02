<script setup lang="ts">
/**
 * Login form — Nuxt port of the React app's `components/auth/user-login-form.tsx`.
 * vee-validate/zod validation mirrors RHF+zodResolver loginFormSchema.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import FormControl from "~/components/ui/form/form-control.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"
import { useAuth } from "~/composables/useAuth"
import { useOAuthConfig } from "~/composables/useOAuthConfig"
import { DEFAULT_AUTH_REDIRECT } from "~/utils/redirect-utils"
import type { LoginFormData } from "~/utils/validation"
import { loginFormSchema } from "~/utils/validation"
import GitHubSignInButton from "./github-signin-button.vue"
import GoogleSignInButton from "./google-signin-button.vue"

const props = defineProps<{
  redirectUrl?: string | null
}>()

const auth = useAuth()
const oauthConfig = useOAuthConfig()

const googleOAuthEnabled = computed(() => oauthConfig.value?.googleEnabled ?? false)
const githubOAuthEnabled = computed(() => oauthConfig.value?.githubEnabled ?? false)
const hasOAuthProviders = computed(() => googleOAuthEnabled.value || githubOAuthEnabled.value)

const finalRedirect = computed(() => props.redirectUrl || DEFAULT_AUTH_REDIRECT)

const form = useForm({
  validationSchema: toTypedSchema(loginFormSchema),
  initialValues: {
    username: "",
    password: "",
  } as LoginFormData,
})

const onSubmit = form.handleSubmit(async (data: LoginFormData) => {
  const { mfaRequired } = await auth.login(data.username, data.password)
  if (mfaRequired) {
    // Preserve redirect through MFA flow
    await navigateTo({ path: "/mfa-challenge", query: { redirect: finalRedirect.value } })
    return
  }
  await navigateTo(finalRedirect.value)
})
</script>

<template>
  <div class="grid gap-6">
    <form
      class="grid gap-4"
      @submit.prevent="onSubmit"
    >
      <FormField v-slot="{ componentField, errorMessage }" name="username">
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              placeholder="name@example.com"
              auto-capitalize="none"
              autocomplete="email"
              auto-correct="off"
              :disabled="auth.isLoading.value"
            />
          </FormControl>
          <FormMessage :error-message="errorMessage" />
        </FormItem>
      </FormField>

      <FormField v-slot="{ componentField, errorMessage }" name="password">
        <FormItem>
          <FormLabel>Password</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              placeholder="Enter your password"
              type="password"
              auto-capitalize="none"
              auto-correct="off"
              autocomplete="current-password"
              :disabled="auth.isLoading.value"
            />
          </FormControl>
          <FormMessage :error-message="errorMessage" />
        </FormItem>
      </FormField>

      <UButton
        type="submit"
        block
        class="mt-2"
        :loading="auth.isLoading.value"
      >
        Sign In
      </UButton>
    </form>

    <template v-if="hasOAuthProviders">
      <USeparator :label="'Or continue with'" />

      <div class="grid gap-2">
        <GitHubSignInButton
          v-if="githubOAuthEnabled"
          variant="signin"
          class="w-full"
          :auth-redirect="finalRedirect"
        />
        <GoogleSignInButton
          v-if="googleOAuthEnabled"
          variant="signin"
          class="w-full"
          :auth-redirect="finalRedirect"
        />
      </div>
    </template>
  </div>
</template>