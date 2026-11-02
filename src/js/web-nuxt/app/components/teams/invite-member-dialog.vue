<script setup lang="ts">
/**
 * InviteMemberDialog — Nuxt port of the React app's
 * `components/teams/invite-member-dialog.tsx`.
 * UModal + vee-validate/zod form sending createTeamInvitation.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { z } from "zod"
import { createTeamInvitation } from "#shared/api/sdk.gen"
import FormControl from "~/components/ui/form/form-control.vue"
import FormDescription from "~/components/ui/form/form-description.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"

const props = defineProps<{
  teamId: string
}>()

const open = defineModel<boolean>("open", { default: false })

const inviteSchema = z.object({
  email: z.email("Please enter a valid email address"),
  role: z.enum(["MEMBER", "ADMIN"]),
})

type InviteFormData = z.infer<typeof inviteSchema>

const rootError = ref<string | null>(null)

const { handleSubmit, isSubmitting, resetForm } = useForm<InviteFormData>({
  validationSchema: toTypedSchema(inviteSchema),
  initialValues: {
    email: "",
    role: "MEMBER",
  } as InviteFormData,
})

const onSubmit = handleSubmit(async (data: InviteFormData) => {
  rootError.value = null
  try {
    await createTeamInvitation({
      path: { team_id: props.teamId },
      body: {
        email: data.email,
        role: data.role,
      },
    })
    await refreshNuxtData(`team-${props.teamId}`)
    await refreshNuxtData(`teamInvitations-${props.teamId}`)
    open.value = false
    resetForm()
  } catch {
    rootError.value = "Failed to send invitation. The user may already be invited."
  }
})

const roleOptions = [
  { value: "MEMBER" as const, label: "Member", description: "Can view and collaborate on team content", icon: "i-lucide-user" },
  { value: "ADMIN" as const, label: "Admin", description: "Can invite members and manage team settings", icon: "i-lucide-shield-check" },
]

const { value: roleValue } = useField<string>("role")
</script>

<template>
  <UModal
    v-model:open="open"
    title="Invite Team Member"
    description="Send an invitation to join this team. They'll receive an email to accept or decline."
  >
    <UButton size="sm" icon="i-lucide-user-plus">Invite</UButton>

    <template #body>
      <form
        class="space-y-5"
        @submit.prevent="onSubmit"
      >
        <FormField
          v-slot="{ componentField, errorMessage }"
          name="email"
        >
          <FormItem>
            <FormLabel>Email address</FormLabel>
            <FormControl>
              <UInput
                v-bind="componentField"
                type="email"
                placeholder="colleague@company.com"
              />
            </FormControl>
            <FormMessage :error-message="errorMessage" />
          </FormItem>
        </FormField>

        <FormField
          v-slot="{ componentField, errorMessage }"
          name="role"
        >
          <FormItem>
            <FormLabel>Role</FormLabel>
            <FormControl>
              <USelect
                :model-value="(componentField as any).modelValue"
                :items="[...roleOptions]"
                placeholder="Select a role"
                icon="i-lucide-user"
                @update:model-value="(v: unknown) => (componentField as any)['onUpdate:modelValue'](v)"
              />
            </FormControl>
            <FormDescription>Choose the permissions level for this member.</FormDescription>
            <FormMessage :error-message="errorMessage" />
          </FormItem>
        </FormField>

        <div
          v-if="rootError"
          class="rounded-md border border-error/20 bg-error/10 p-3"
        >
          <p class="text-sm text-error">{{ rootError }}</p>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <UButton
            type="button"
            variant="ghost"
            color="neutral"
            @click="open = false"
          >
            Cancel
          </UButton>
          <UButton
            type="submit"
            :loading="isSubmitting"
          >
            {{ isSubmitting ? "Sending..." : "Send Invitation" }}
          </UButton>
        </div>
      </form>
    </template>
  </UModal>
</template>