<script setup lang="ts">
/**
 * CreateTeamForm — Nuxt port of the React app's
 * `components/teams/create-team-form.tsx`.
 * vee-validate/zod validation mirrors RHF+zodResolver; tag input with
 * suggestions from listTags mirrors the React tag UX.
 */
import { toTypedSchema } from "@vee-validate/zod"
import { useForm } from "vee-validate"
import { z } from "zod"
import { createTeam, listTags } from "#shared/api/sdk.gen"
import FormControl from "~/components/ui/form/form-control.vue"
import FormDescription from "~/components/ui/form/form-description.vue"
import FormField from "~/components/ui/form/form-field.vue"
import FormItem from "~/components/ui/form/form-item.vue"
import FormLabel from "~/components/ui/form/form-label.vue"
import FormMessage from "~/components/ui/form/form-message.vue"

const createTeamSchema = z.object({
  name: z.string().min(1, "Team name is required"),
  description: z.string().optional(),
})

type CreateTeamFormData = z.infer<typeof createTeamSchema>

const selectedTags = ref<string[]>([])
const tagInput = ref("")

const { data: existingTagsData } = await useAsyncData("tags", async () => {
  const response = await listTags()
  return response.data?.items ?? []
})
const existingTags = computed(() => existingTagsData.value ?? [])

const { handleSubmit, isSubmitting, setErrors } = useForm<CreateTeamFormData>({
  validationSchema: toTypedSchema(createTeamSchema),
  initialValues: {
    name: "",
    description: "",
  } as CreateTeamFormData,
})

const addTag = (tagName: string) => {
  const trimmed = tagName.trim().toLowerCase()
  if (trimmed && !selectedTags.value.includes(trimmed)) {
    selectedTags.value = [...selectedTags.value, trimmed]
  }
  tagInput.value = ""
}

const removeTag = (tag: string) => {
  selectedTags.value = selectedTags.value.filter((t) => t !== tag)
}

const handleTagKeyDown = (e: KeyboardEvent) => {
  if (e.key === "Enter" || e.key === ",") {
    e.preventDefault()
    addTag(tagInput.value)
  }
}

// Filter suggestions based on input
const tagSuggestions = computed(() =>
  existingTags.value.filter((tag) => tag.name.toLowerCase().includes(tagInput.value.toLowerCase()) && !selectedTags.value.includes(tag.name.toLowerCase())),
)

const onSubmit = handleSubmit(async (data: CreateTeamFormData) => {
  try {
    await createTeam({
      body: {
        name: data.name,
        description: data.description,
        tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
      },
    })
    await navigateTo("/teams")
  } catch {
    setErrors({ name: undefined })
    useToast().add({ title: "Failed to create team", color: "error", icon: "i-lucide-circle-alert" })
  }
})
</script>

<template>
  <form
    class="space-y-6"
    @submit.prevent="onSubmit"
  >
    <FormField
      v-slot="{ componentField, errorMessage }"
      name="name"
    >
      <FormItem>
        <FormLabel>Team Name</FormLabel>
        <FormControl>
          <UInput
            v-bind="componentField"
            placeholder="Engineering"
          />
        </FormControl>
        <FormMessage :error-message="errorMessage" />
      </FormItem>
    </FormField>

    <FormField
      v-slot="{ componentField, errorMessage }"
      name="description"
    >
      <FormItem>
        <FormLabel>Description</FormLabel>
        <FormControl>
          <UTextarea
            v-bind="componentField"
            placeholder="What does this team do?"
            :rows="3"
            class="resize-none"
          />
        </FormControl>
        <FormMessage :error-message="errorMessage" />
      </FormItem>
    </FormField>

    <!-- Tags -->
    <FormItem>
      <FormLabel>Tags</FormLabel>
      <FormDescription class="mb-2">Categorize your team for easier discovery</FormDescription>
      <FormControl>
        <div class="space-y-3">
          <div class="relative">
            <UInput
              v-model="tagInput"
              placeholder="Type a tag and press Enter..."
              class="pr-10"
              @keydown="handleTagKeyDown"
              @blur="tagInput && addTag(tagInput)"
            />
            <UButton
              v-if="tagInput"
              type="button"
              variant="ghost"
              size="sm"
              class="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 p-0"
              icon="i-lucide-plus"
              aria-label="Add tag"
              @click="addTag(tagInput)"
            />
            <div
              v-if="tagInput && tagSuggestions.length > 0"
              class="absolute z-10 mt-1 w-full rounded-md border border-border bg-popover p-1 shadow-lg"
            >
              <button
                v-for="tag in tagSuggestions.slice(0, 5)"
                :key="tag.id"
                type="button"
                class="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm hover:bg-accent"
                @click="addTag(tag.name)"
              >
                <span class="text-muted-foreground">#</span>
                {{ tag.name }}
              </button>
            </div>
          </div>

          <div
            v-if="selectedTags.length > 0"
            class="flex flex-wrap gap-2"
          >
            <UBadge
              v-for="tag in selectedTags"
              :key="tag"
              variant="secondary"
              class="gap-1.5 py-1 pr-1 pl-2.5"
            >
              <span class="text-muted-foreground">#</span>
              {{ tag }}
              <button
                type="button"
                class="ml-0.5 rounded-full p-0.5 transition-colors hover:bg-muted-foreground/20"
                :aria-label="`Remove ${tag}`"
                @click="removeTag(tag)"
              >
                <UIcon
                  name="i-lucide-x"
                  class="h-3 w-3"
                />
              </button>
            </UBadge>
          </div>
        </div>
      </FormControl>
    </FormItem>

    <USeparator />

    <div class="flex items-center justify-between">
      <UButton
        type="button"
        variant="ghost"
        color="neutral"
        to="/teams"
      >
        Cancel
      </UButton>
      <UButton
        type="submit"
        :loading="isSubmitting"
      >
        {{ isSubmitting ? "Creating..." : "Create Team" }}
      </UButton>
    </div>
  </form>
</template>