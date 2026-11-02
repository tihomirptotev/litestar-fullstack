<script setup lang="ts">
/**
 * Reset password page — Nuxt port of the React app's
 * `routes/_public/reset-password.tsx`.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { z } from "zod"
import { resetPassword } from "#shared/api/sdk.gen"
import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import FormControl from "~/components/ui/form/form-control.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"
import PasswordStrength from "~/components/ui/password-strength.vue"
import { validatePassword } from "~/utils/password-strength"

useHead({ title: "Reset password — Litestar Fullstack" })

definePageMeta({ layout: false })

const route = useRoute()
const toast = useToast()

const token = computed(() => (route.query.token as string | undefined) || "")

const isSuccess = ref(false)
const isPending = ref(false)

const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(1, "Password is required")
      .superRefine((value, ctx) => {
        const error = validatePassword(value)
        if (error) {
          ctx.addIssue({ code: "custom", message: error })
        }
      }),
    confirmPassword: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

const form = useForm({
  validationSchema: toTypedSchema(resetPasswordSchema),
  initialValues: {
    password: "",
    confirmPassword: "",
  },
})

const password = computed(() => form.values.password ?? "")

const onSubmit = form.handleSubmit(async (data) => {
  if (!token.value) {
    toast.add({ title: "Reset token is missing", color: "error" })
    return
  }
  isPending.value = true
  try {
    await resetPassword({
      body: {
        token: token.value,
        password: data.password,
        password_confirm: data.confirmPassword,
      },
    })
    isSuccess.value = true
    toast.add({ title: "Password reset successfully!", color: "success" })
    setTimeout(() => {
      navigateTo("/login")
    }, 3000)
  } catch (error: unknown) {
    const message = (error as Error).message || "Failed to reset password"
    if (message.includes("expired") || message.includes("invalid")) {
      toast.add({ title: "This reset link has expired or is invalid. Please request a new one.", color: "error" })
    } else {
      toast.add({ title: message, color: "error" })
    }
  } finally {
    isPending.value = false
  }
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <AuthHeroPanel
      :show-testimonial="false"
      description="Secure password recovery for your account."
    />

    <div class="flex flex-1 flex-col items-center justify-center bg-brand-gray-light px-4 py-12 dark:bg-background">
      <div class="w-full max-w-md space-y-6">
        <!-- Invalid / missing token -->
        <template v-if="!token">
          <div class="text-center">
            <h1 class="text-2xl font-semibold tracking-tight">
              Invalid Reset Link
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              This password reset link is invalid or incomplete.
            </p>
          </div>
          <UAlert
            icon="i-lucide-circle-alert"
            variant="subtle"
            color="error"
            :title="'Please request a new password reset link.'"
          />
          <UButton
            block
            to="/forgot-password"
          >
            Request new reset link
          </UButton>
        </template>

        <!-- Success -->
        <template v-else-if="isSuccess">
          <div class="text-center">
            <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
              <UIcon
                name="i-lucide-circle-check"
                class="h-6 w-6 text-green-600 dark:text-green-400"
              />
            </div>
            <h1 class="text-2xl font-semibold tracking-tight">
              Password Reset Successfully
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Your password has been reset. Redirecting to login...
            </p>
          </div>
          <UButton
            block
            to="/login"
          >
            Go to login
          </UButton>
        </template>

        <!-- Form -->
        <template v-else>
          <div class="text-center">
            <h1 class="text-2xl font-semibold tracking-tight">
              Reset your password
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Enter your new password below
            </p>
          </div>

          <form
            class="space-y-4"
            @submit.prevent="onSubmit"
          >
            <FormField
              v-slot="{ componentField, errorMessage }"
              name="password"
            >
              <FormItem>
                <FormLabel>New Password</FormLabel>
                <FormControl>
                  <UInput
                    v-bind="componentField"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Enter new password"
                    :ui="{ trailing: 'pe-1' }"
                  >
                    <template #trailing>
                      <UButton
                        color="neutral"
                        variant="ghost"
                        size="xs"
                        :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                        :aria-label="showPassword ? 'Hide password' : 'Show password'"
                        :padded="false"
                        @click="showPassword = !showPassword"
                      />
                    </template>
                  </UInput>
                </FormControl>
                <PasswordStrength
                  v-if="password"
                  :password="password"
                  class="pt-2"
                />
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
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Confirm new password"
                    :ui="{ trailing: 'pe-1' }"
                  >
                    <template #trailing>
                      <UButton
                        color="neutral"
                        variant="ghost"
                        size="xs"
                        :icon="showConfirmPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                        :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
                        :padded="false"
                        @click="showConfirmPassword = !showConfirmPassword"
                      />
                    </template>
                  </UInput>
                </FormControl>
                <FormMessage :error-message="errorMessage" />
              </FormItem>
            </FormField>

            <UButton
              type="submit"
              block
              :loading="isPending"
            >
              {{ isPending ? "Resetting..." : "Reset password" }}
            </UButton>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>