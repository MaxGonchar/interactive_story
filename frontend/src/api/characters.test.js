import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getCharacters } from './characters'

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

describe('api/characters', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('getCharacters', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk([]))
      await getCharacters('story-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/characters`,
        undefined
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(getCharacters('story-1')).rejects.toThrow('Not found')
    })
  })
})
