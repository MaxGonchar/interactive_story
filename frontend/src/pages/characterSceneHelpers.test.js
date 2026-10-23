import { describe, expect, it } from 'vitest'
import {
  buildScenePrefill,
  deriveModelDefaults,
} from './characterSceneHelpers'
import {
  makeCharacterScene,
  makeCharacterSceneItem,
  makeModelRegistry,
} from '../tests/factories'

const registry = makeModelRegistry({
  default_model_id: 'default-model',
  models: {
    'default-model': { name: 'Default Model' },
    'character-model': { name: 'Character Model' },
    'narrator-model': { name: 'Narrator Model' },
  },
})

describe('deriveModelDefaults', () => {
  it('uses the latest narrator model and latest non-null character model', () => {
    const items = [
      makeCharacterSceneItem({
        llm_data: {
          character_model_id: 'character-model',
          narrator_model_id: 'narrator-model',
        },
      }),
      makeCharacterSceneItem({
        llm_data: {
          character_model_id: null,
          narrator_model_id: 'default-model',
        },
      }),
    ]

    const result = deriveModelDefaults(items, registry)

    expect(result).toEqual({
      characterModelId: 'character-model',
      narratorModelId: 'default-model',
    })
  })

  it('falls back independently when a derived model is not in the registry', () => {
    const items = [
      makeCharacterSceneItem({
        llm_data: {
          character_model_id: 'removed-character-model',
          narrator_model_id: 'narrator-model',
        },
      }),
    ]

    const result = deriveModelDefaults(items, registry)

    expect(result).toEqual({
      characterModelId: 'default-model',
      narratorModelId: 'narrator-model',
    })
  })

  it('uses the registry default for empty items', () => {
    const result = deriveModelDefaults([], registry)

    expect(result).toEqual({
      characterModelId: 'default-model',
      narratorModelId: 'default-model',
    })
  })
})

describe('buildScenePrefill', () => {
  it('combines prior context and summary with style and the last narration', () => {
    const previousScene = makeCharacterScene({
      context: ['The ship reaches the harbor.'],
      scene_summary: ['The crew discovers a hidden signal.'],
      scene_description: {
        general_scene_guide: 'Do not copy this.',
        writing_style: 'Cinematic prose.',
      },
      items: [
        makeCharacterSceneItem({ narration: 'A bell rings.' }),
        makeCharacterSceneItem({ narration: 'Fog closes around the pier.' }),
      ],
    })

    const result = buildScenePrefill(previousScene)

    expect(result).toEqual({
      context: [
        'The ship reaches the harbor.',
        'The crew discovers a hidden signal.',
      ],
      writingStyle: 'Cinematic prose.',
      firstMessage: 'Fog closes around the pier.',
    })
  })

  it('returns empty prefill values when previous scene content is missing', () => {
    const result = buildScenePrefill(makeCharacterScene())

    expect(result).toEqual({
      context: [],
      writingStyle: '',
      firstMessage: '',
    })
  })
})
