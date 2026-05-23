import { describe, it, expect } from 'vitest'

import { unwrapBlobError } from '../blob'

/** Build an axios-like error whose `response.data` is a Blob (responseType:'blob'). */
function blobError(status: number, body: string, type = 'application/json') {
  return {
    response: {
      status,
      data: new Blob([body], { type }),
    },
    message: `Request failed with status code ${status}`,
  }
}

describe('unwrapBlobError', () => {
  it('parses an APIResponse "message" from a 4xx blob body', async () => {
    const err = blobError(403, JSON.stringify({ message: 'No tienes permiso (PL gate).' }))
    const result = await unwrapBlobError(err)
    expect(result).toBeInstanceOf(Error)
    expect((result as Error).message).toBe('No tienes permiso (PL gate).')
  })

  it('falls back to "detail" when there is no "message"', async () => {
    const err = blobError(404, JSON.stringify({ detail: 'No encontrado.' }))
    const result = await unwrapBlobError(err)
    expect((result as Error).message).toBe('No encontrado.')
  })

  it('handles 5xx blob bodies too', async () => {
    const err = blobError(500, JSON.stringify({ message: 'Error interno.' }))
    const result = await unwrapBlobError(err)
    expect((result as Error).message).toBe('Error interno.')
  })

  it('returns the original error when the blob is not valid JSON', async () => {
    const err = blobError(400, 'not-json-at-all')
    const result = await unwrapBlobError(err)
    expect(result).toBe(err)
  })

  it('returns the original error when JSON has no message/detail', async () => {
    const err = blobError(400, JSON.stringify({ foo: 'bar' }))
    const result = await unwrapBlobError(err)
    expect(result).toBe(err)
  })

  it('returns the original error for non-blob response data', async () => {
    const err = { response: { status: 400, data: { message: 'plain object' } } }
    const result = await unwrapBlobError(err)
    expect(result).toBe(err)
  })

  it('returns the original error for a 2xx/3xx status', async () => {
    const err = blobError(302, JSON.stringify({ message: 'redirect' }))
    const result = await unwrapBlobError(err)
    expect(result).toBe(err)
  })

  it('returns the original error when there is no response (network error)', async () => {
    const err = new Error('Network Error')
    const result = await unwrapBlobError(err)
    expect(result).toBe(err)
  })
})
