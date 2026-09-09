import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getModels } from './models'

const BASE_URL = 'http://localhost:8000'

function mockFetchOk(data) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  })
}

function mockFetchError(message) {
  return vi.fn().mockResolvedValue({
    ok: false,
    json: () => Promise.resolve({ error: { message } }),
  })
}

describe('api/models', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls the models endpoint with GET', async () => {
    vi.stubGlobal('fetch', mockFetchOk({}))

    await getModels()

    expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/api/models`, undefined)
  })

  it('throws the API error message on non-ok response', async () => {
    vi.stubGlobal('fetch', mockFetchError('Models unavailable'))

    await expect(getModels()).rejects.toThrow('Models unavailable')
  })
})