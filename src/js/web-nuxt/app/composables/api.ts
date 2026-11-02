/**
 * Typed wrappers around the generated hey-api SDK functions, adapted for
 * Nuxt's data-fetching composables (useAsyncData/useFetch) — the Nuxt
 * equivalent of the React app's TanStack Query hook wrappers in
 * `src/lib/api/hooks/`.
 *
 * The SDK functions return `{ data, error, response }` (fields style,
 * throwOnError: false). These helpers:
 * - unwrap `data` or throw the `error` — so `useAsyncData` surfaces errors
 *   naturally
 * - cast away the generated `Response` union where the OpenAPI spec
 *   over-approximates response shapes
 */
import type { Options, RequestResult } from "#shared/api/client"

type FieldsResult<TData, TError> = RequestResult<TData, TError, false>

/**
 * Unwrap a SDK call's `data` field, throwing the error on failure.
 * Designed for use inside `useAsyncData` handlers.
 */
export async function unwrap<TData, TError>(call: FieldsResult<TData, TError>): Promise<TData> {
  const result = await call
  if (result.error) {
    throw result.error
  }
  return result.data
}

/**
 * Unwrap and cast — for endpoints where the generated response type is a
 * union that we know narrows in practice (e.g. LoginResponse).
 */
export async function unwrapAs<TData, TError, TAs = TData>(call: FieldsResult<TData, TError>): Promise<TAs> {
  const result = await call
  if (result.error) {
    throw result.error
  }
  return result.data as TAs
}

/** Extract a human-readable message from an API error object. */
export function apiErrorMessage(error: unknown): string {
  if (typeof error === "string") {
    return error
  }
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as { detail?: unknown }).detail
    if (typeof detail === "string") {
      return detail
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return "An error occurred"
}

export type { Options }
