<script setup lang="ts">
/**
 * Forgot password page — Nuxt port of the React app's
 * `routes/_public/forgot-password.tsx`.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { z } from "zod"
import { forgotPassword } from "#shared/api/sdk.gen"
import AuthHeroPanel from "~/components/auth/auth-hero-panel.vue"
import FormControl from "~/components/ui/form/form-control.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"

useHead({ title: "Forgot password — Litestar Fullstack" })

definePageMeta({ layout: false })

const toast = useToast()

const isSuccess = ref(false)
const submittedEmail = ref("")

const forgotPasswordSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
})

const form = useForm({
  validationSchema: toTypedSchema(forgotPasswordSchema),
  initialValues: { email: "" },
})

const isPending = ref(false)

const onSubmit = form.handleSubmit(async (data) => {
  isPending.value = true
  try {
    await forgotPassword({ body: { email: data.email } })
    submittedEmail.value = data.email
    isSuccess.value = true
    toast.add({ title: "Password reset email sent!", color: "success" })
  } catch (error: unknown) {
    const message = (error as Error).message || "Failed to send reset email"
    // Don't reveal if email exists or not for security
    if (message.includes("not found")) {
      submittedEmail.value = data.email
      isSuccess.value = true
      toast.add({ title: "If an account exists, a reset email has been sent", color: "success" })
    } else {
      toast.add({ title: message, color: "error" })
    }
  } finally {
    isPending.value = false
  }
})

const sendAnother = () => {
  isSuccess.value = false
  form.resetForm()
}
</script>

<template>
  <div class="relative flex min-h-screen w-full">
    <AuthHeroPanel
      :show-testimonial="false"
      description="Secure password recovery for your account."
    />

    <div class="flex flex-1 flex-col items-center justify-center bg-brand-gray-light px-4 py-12 dark:bg-background">
      <div class="w-full max-w-md space-y-6">
        <!-- Success state -->
        <template v-if="isSuccess">
          <div class="text-center">
            <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
              <UIcon
                name="i-lucide-circle-check"
                class="h-6 w-6 text-green-600 dark:text-green-400"
              />
            </div>
            <h1 class="text-2xl font-semibold tracking-tight">
              Check your email
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              We sent a reset link to <strong>{{ submittedEmail }}</strong>
            </p>
          </div>

          <UAlert
            icon="i-lucide-mail"
            variant="subtle"
            :title="'Links expire in one hour. Check spam or request another email if needed.'"
          />

          <div class="space-y-2">
            <UButton
              variant="outline"
              color="neutral"
              block
              @click="sendAnother"
            >
              Send another email
            </UButton>
            <UButton
              variant="ghost"
              color="neutral"
              block
              icon="i-lucide-arrow-left"
              to="/login"
            >
              Back to login
            </UButton>
          </div>
        </template>

        <!-- Form state -->
        <template v-else>
          <div class="text-center">
            <h1 class="text-2xl font-semibold tracking-tight">
              Forgot your password?
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Enter your email and we'll send you a reset link.
            </p>
          </div>

          <form
            class="space-y-4"
            @submit.prevent="onSubmit"
          >
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
                    placeholder="you@example.com"
                    autocomplete="email"
                  />
                </FormControl>
                <FormMessage :error-message="errorMessage" />
              </FormItem>
            </FormField>

            <UButton
              type="submit"
              block
              :loading="isPending"
            >
              {{ isPending ? "Sending..." : "Send reset email" }}
            </UButton>
          </form>

          <UButton
            variant="ghost"
            color="neutral"
            block
            icon="i-lucide-arrow-left"
            to="/login"
          >
            Back to login
          </UButton>
        </template>
      </div>
    </div>
  </div>
</template>