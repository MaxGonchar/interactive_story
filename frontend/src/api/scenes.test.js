import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getScene,
  playScene,
  editMessage,
  deleteMessage,
  finishScene,
  regenerateLastAssistantMessage,
  generateSceneSummary,
} from './scenes'

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

describe('api/scenes', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('getScene', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await getScene('story-1', 'scene-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1`,
        undefined
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(getScene('story-1', 'scene-1')).rejects.toThrow('Not found')
    })
  })

  describe('playScene', () => {
    it('calls correct URL with POST and correct JSON body', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await playScene('story-1', 'scene-1', 'hello')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/play`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: 'hello' }),
        }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Bad request'))
      await expect(playScene('story-1', 'scene-1', 'hello')).rejects.toThrow('Bad request')
    })
  })

  describe('editMessage', () => {
    it('calls correct URL with PUT and correct JSON body', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await editMessage('story-1', 'scene-1', 'msg-1', 'new content')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/messages/msg-1`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: 'new content' }),
        }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Forbidden'))
      await expect(editMessage('story-1', 'scene-1', 'msg-1', 'x')).rejects.toThrow('Forbidden')
    })
  })

  describe('deleteMessage', () => {
    it('calls correct URL with DELETE', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await deleteMessage('story-1', 'scene-1', 'msg-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/messages/msg-1`,
        { method: 'DELETE' }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(deleteMessage('story-1', 'scene-1', 'msg-1')).rejects.toThrow('Not found')
    })
  })

  describe('finishScene', () => {
    it('calls correct URL with POST and correct JSON body', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await finishScene('story-1', 'scene-1', ['summary item'])
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/finish`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scene_summary: ['summary item'] }),
        }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Server error'))
      await expect(finishScene('story-1', 'scene-1', [])).rejects.toThrow('Server error')
    })
  })

  describe('regenerateLastAssistantMessage', () => {
    it('calls correct URL with POST', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await regenerateLastAssistantMessage('story-1', 'scene-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/regenerate`,
        { method: 'POST' }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Error'))
      await expect(regenerateLastAssistantMessage('story-1', 'scene-1')).rejects.toThrow('Error')
    })
  })

  describe('generateSceneSummary', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await generateSceneSummary('story-1', 'scene-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/scenes/scene-1/summarize`,
        undefined
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Unavailable'))
      await expect(generateSceneSummary('story-1', 'scene-1')).rejects.toThrow('Unavailable')
    })
  })
})
