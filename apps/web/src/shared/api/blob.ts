/**
 * Blob-download error helper (V4-3).
 *
 * When a request uses `responseType: 'blob'` and the backend responds with a
 * 4xx/5xx error, axios still hands back the error body as a `Blob` — so the
 * usual `error.response.data.message` is an unreadable Blob and the UI shows a
 * generic "Request failed with status code 4xx". This helper reads that Blob,
 * parses the wrapped APIResponse JSON, and returns a friendly `Error` to throw.
 *
 * Extracted from the inline logic in `dossierService.downloadConsolidatedPdf`
 * (commit ebb039b9) so every blob-download service shares one implementation.
 *
 * Usage — keep the original throw semantics, one statement:
 *
 *   try {
 *     const r = await apiClient.get<Blob>(url, { responseType: 'blob' })
 *     return r.data
 *   } catch (err) {
 *     throw await unwrapBlobError(err)
 *   }
 *
 * Returns the parsed `Error(message)` when the body is a JSON APIResponse with a
 * message/detail; otherwise returns the original error unchanged so callers
 * still surface the native axios error.
 */
export async function unwrapBlobError(err: unknown): Promise<unknown> {
  const e = err as { response?: { status?: number; data?: unknown } }
  const status = e?.response?.status
  const data = e?.response?.data
  if (status && status >= 400 && data instanceof Blob) {
    // Parse first; never throw inside this try or the catch below would swallow
    // the friendly message and we'd fall through to the original error.
    let parsed: { message?: string; detail?: string } | null = null
    try {
      parsed = JSON.parse(await data.text()) as { message?: string; detail?: string }
    } catch {
      parsed = null
    }
    const message = parsed?.message ?? parsed?.detail
    if (message) {
      return new Error(message)
    }
  }
  return err
}
