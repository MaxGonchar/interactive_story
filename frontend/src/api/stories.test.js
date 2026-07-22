import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getStories, getStory } from './stories'

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

describe('api/stories', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('getStories', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk([]))
      await getStories()
      expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/api/stories`, undefined)
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Server error'))
      await expect(getStories()).rejects.toThrow('Server error')
    })
  })

  describe('getStory', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await getStory('story-1')
      expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/api/stories/story-1`, undefined)
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(getStory('story-1')).rejects.toThrow('Not found')
    })
  })
})
