import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getChoiceDrivenPlay,
  generateChoices,
  regenerateChoices,
  selectChoice,
  editStepText,
  returnToStep,
} from './choice_driven'

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

describe('api/choice_driven', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('getChoiceDrivenPlay', () => {
    it('calls correct URL with GET', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await getChoiceDrivenPlay('story-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play`,
        undefined
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(getChoiceDrivenPlay('story-1')).rejects.toThrow('Not found')
    })
  })

  describe('generateChoices', () => {
    it('calls correct URL with POST', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await generateChoices('story-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play/generate-choices`,
        { method: 'POST' }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Failed'))
      await expect(generateChoices('story-1')).rejects.toThrow('Failed')
    })
  })

  describe('regenerateChoices', () => {
    it('calls correct URL with POST', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await regenerateChoices('story-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play/regenerate-choices`,
        { method: 'POST' }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Failed'))
      await expect(regenerateChoices('story-1')).rejects.toThrow('Failed')
    })
  })

  describe('selectChoice', () => {
    it('calls correct URL with POST and correct JSON body', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await selectChoice('story-1', 'attack', 'enemy defeated')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play/select-choice`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'attack', consequence: 'enemy defeated' }),
        }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Bad request'))
      await expect(selectChoice('story-1', 'x', 'y')).rejects.toThrow('Bad request')
    })
  })

  describe('editStepText', () => {
    it('calls correct URL with PATCH and correct JSON body', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await editStepText('story-1', 'step-1', 'new text')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play/steps/step-1`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: 'new text' }),
        }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Not found'))
      await expect(editStepText('story-1', 'step-1', 'x')).rejects.toThrow('Not found')
    })
  })

  describe('returnToStep', () => {
    it('calls correct URL with DELETE', async () => {
      vi.stubGlobal('fetch', mockFetchOk({}))
      await returnToStep('story-1', 'step-1')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api/stories/story-1/choice-play/steps/step-1/forward`,
        { method: 'DELETE' }
      )
    })

    it('throws with API error message on non-ok response', async () => {
      vi.stubGlobal('fetch', mockFetchError('Forbidden'))
      await expect(returnToStep('story-1', 'step-1')).rejects.toThrow('Forbidden')
    })
  })
})
