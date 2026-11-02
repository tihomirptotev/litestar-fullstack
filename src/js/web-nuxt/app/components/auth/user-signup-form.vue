<script setup lang="ts">
/**
 * Signup form — Nuxt port of the React app's
 * `components/auth/user-signup-form.tsx`.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { z } from "zod"
import { accountRegister } from "#shared/api/sdk.gen"
import FormControl from "~/components/ui/form/form-control.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"
import PasswordStrength from "~/components/ui/password-strength.vue"
import { useAuth } from "~/composables/useAuth"
import { useOAuthConfig } from "~/composables/useOAuthConfig"
import { validatePassword } from "~/utils/password-strength"
import { DEFAULT_AUTH_REDIRECT } from "~/utils/redirect-utils"
import GitHubSignInButton from "./github-signin-button.vue"
import GoogleSignInButton from "./google-signin-button.vue"

const props = defineProps<{
  redirectUrl?: string | null
}>()

const toast = useToast()
const auth = useAuth()
const oauthConfig = useOAuthConfig()

const googleOAuthEnabled = computed(() => oauthConfig.value?.googleEnabled ?? false)
const githubOAuthEnabled = computed(() => oauthConfig.value?.githubEnabled ?? false)
const hasOAuthProviders = computed(() => googleOAuthEnabled.value || githubOAuthEnabled.value)

const finalRedirect = computed(() => props.redirectUrl || DEFAULT_AUTH_REDIRECT)

const signupSchema = z
  .object({
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(1, "Password is required")
      .superRefine((value, ctx) => {
        const error = validatePassword(value)
        if (error) {
          ctx.addIssue({ code: "custom", message: error })
        }
      }),
    name: z.string().min(1, "Name is required"),
    confirmPassword: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

const form = useForm({
  validationSchema: toTypedSchema(signupSchema),
  initialValues: {
    email: "",
    password: "",
    name: "",
    confirmPassword: "",
  },
})

const passwordValue = computed(() => (form.values.password as string) ?? "")

const isPending = computed(() => auth.isLoading.value)

const onSubmit = form.handleSubmit(async (data) => {
  try {
    const response = await accountRegister({
      body: { email: data.email, password: data.password, name: data.name },
    })

    if (response.data) {
      toast.add({ title: "Account created! Please check your email to verify your account.", color: "success" })
      // Preserve redirect URL when navigating to login
      await navigateTo({
        path: "/login",
        query: props.redirectUrl ? { redirect: props.redirectUrl } : {},
      })
      return
    }

    toast.add({ title: response.error?.detail || "Signup failed", color: "error" })
  } catch {
    toast.add({ title: "An error occurred during signup", color: "error" })
  }
})

void isPending
</script>

<template>
  <div class="grid gap-6">
    <form
      class="grid gap-4"
      @submit.prevent="onSubmit"
    >
      <FormField
        v-slot="{ componentField, errorMessage }"
        name="name"
      >
        <FormItem>
          <FormLabel>Name</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              placeholder="Enter your name"
              auto-capitalize="none"
              autocomplete="name"
              auto-correct="off"
              :disabled="auth.isLoading.value"
            />
          </FormControl>
          <FormMessage :error-message="errorMessage" />
        </FormItem>
      </FormField>

      <FormField
        v-slot="{ componentField, errorMessage }"
        name="email"
      >
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              type="email"
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

      <FormField
        v-slot="{ componentField, errorMessage }"
        name="password"
      >
        <FormItem>
          <FormLabel>Password</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              type="password"
              placeholder="Create a password"
              auto-capitalize="none"
              autocomplete="new-password"
              auto-correct="off"
              :disabled="auth.isLoading.value"
            />
          </FormControl>
          <PasswordStrength :password="passwordValue" />
          <FormMessage :error-message="errorMessage" />
        </FormItem>
      </FormField>

      <FormField
        v-slot="{ componentField, errorMessage }"
        name="confirmPassword"
      >
        <FormItem>
          <FormLabel>Confirm Password</FormLabel>
          <FormControl>
            <UInput
              v-bind="componentField"
              type="password"
              placeholder="Confirm your password"
              auto-capitalize="none"
              autocomplete="new-password"
              auto-correct="off"
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
        Create Account
      </UButton>
    </form>

    <template v-if="hasOAuthProviders">
      <USeparator label="Or continue with" />

      <div class="grid gap-2">
        <GitHubSignInButton
          v-if="githubOAuthEnabled"
          variant="signup"
          :auth-redirect="finalRedirect"
        />
        <GoogleSignInButton
          v-if="googleOAuthEnabled"
          variant="signup"
          :auth-redirect="finalRedirect"
        />
      </div>
    </template>
  </div>
</template>