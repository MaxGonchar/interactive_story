import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  createCharacterScene,
  deleteCharacterSceneItem,
  editCharacterSceneItem,
  finishCharacterScene,
  getCharacterMemoryDraft,
  getCharacterScene,
  getCharacterSceneSummaryDraft,
  replaceCharacterTurn,
  submitCharacterTurn,
} from './character_play'

const BASE_URL = 'http://localhost:8000'
const responseData = { data: { id: 1 } }

const scenePayload = {
  user_character_id: null,
  character_ids: ['navigator'],
  context: ['The ship reached the harbor.'],
  general_scene_guide: 'Keep tension rising.',
  writing_style: 'Cinematic and concise.',
  first_message: 'A bell rings through the fog.',
  character_model_id: 'character-model',
  narrator_model_id: 'narrator-model',
}
const playerTurnPayload = {
  actor: { type: 'player' },
  action: 'I look for the nearest light source.',
  character_model_id: 'character-model',
  narrator_model_id: 'narrator-model',
}
const finishMemoryUpdates = { navigator: ['The captain trusted the warning.'] }

const endpointCalls = [
  {
    name: 'createCharacterScene',
    call: () => createCharacterScene('story-1', scenePayload),
    url: '/api/stories/story-1/character-play/scenes',
    options: {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenePayload),
    },
  },
  {
    name: 'getCharacterScene',
    call: () => getCharacterScene('story-1', 'scene-1'),
    url: '/api/stories/story-1/character-play/scenes/scene-1',
    options: undefined,
  },
  {
    name: 'submitCharacterTurn',
    call: () => submitCharacterTurn('story-1', 'scene-1', playerTurnPayload),
    url: '/api/stories/story-1/character-play/scenes/scene-1/turns',
    options: {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(playerTurnPayload),
    },
  },
  {
    name: 'replaceCharacterTurn',
    call: () =>
      replaceCharacterTurn('story-1', 'scene-1', 'item-2', playerTurnPayload),
    url: '/api/stories/story-1/character-play/scenes/scene-1/turns/item-2/replace',
    options: {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(playerTurnPayload),
    },
  },
  {
    name: 'editCharacterSceneItem',
    call: () =>
      editCharacterSceneItem(
        'story-1',
        'scene-1',
        'item-2',
        'The captain turns toward a wavering light.'
      ),
    url: '/api/stories/story-1/character-play/scenes/scene-1/items/item-2',
    options: {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        narration: 'The captain turns toward a wavering light.',
      }),
    },
  },
  {
    name: 'deleteCharacterSceneItem',
    call: () => deleteCharacterSceneItem('story-1', 'scene-1', 'item-2'),
    url: '/api/stories/story-1/character-play/scenes/scene-1/items/item-2',
    options: { method: 'DELETE' },
  },
  {
    name: 'getCharacterSceneSummaryDraft',
    call: () => getCharacterSceneSummaryDraft('story-1', 'scene-1'),
    url: '/api/stories/story-1/character-play/scenes/scene-1/summary/draft',
    options: undefined,
  },
  {
    name: 'getCharacterMemoryDraft',
    call: () => getCharacterMemoryDraft('story-1', 'scene-1', 'navigator'),
    url: '/api/stories/story-1/character-play/scenes/scene-1/characters/navigator/memory/draft',
    options: undefined,
  },
  {
    name: 'finishCharacterScene',
    call: () =>
      finishCharacterScene(
        'story-1',
        'scene-1',
        ['The crew uncovered a betrayal.'],
        finishMemoryUpdates
      ),
    url: '/api/stories/story-1/character-play/scenes/scene-1/finish',
    options: {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scene_summary: ['The crew uncovered a betrayal.'],
        character_memory_updates: finishMemoryUpdates,
      }),
    },
  },
]

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

describe('api/character_play', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it.each(endpointCalls)('$name calls its documented endpoint', async (endpoint) => {
    vi.stubGlobal('fetch', mockFetchOk(responseData))

    await expect(endpoint.call()).resolves.toEqual(responseData)
    expect(fetch).toHaveBeenCalledWith(
      `${BASE_URL}${endpoint.url}`,
      endpoint.options
    )
  })

  it.each(endpointCalls)('$name surfaces API errors on non-2xx responses', async (endpoint) => {
    vi.stubGlobal('fetch', mockFetchError('Request failed'))

    await expect(endpoint.call()).rejects.toThrow('Request failed')
  })
})
