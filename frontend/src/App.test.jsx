import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, it, expect, vi } from 'vitest'
import { getCharacters } from './api/characters'
import { getModels } from './api/models'
import { getStory } from './api/stories'
import { makeCharacter, makeModel, makeModelRegistry, makeStory } from './tests/factories'
import App from './App'

vi.mock('./api/characters')
vi.mock('./api/models')
vi.mock('./api/stories')

afterEach(() => {
  cleanup()
  window.history.replaceState({}, '', '/')
})

beforeEach(() => {
  vi.resetAllMocks()
})

describe('App character-scene routes', () => {
  it('renders the character-scene creation page', async () => {
    window.history.replaceState({}, '', '/stories/story-1/character-scenes/new')
    getStory.mockResolvedValue({
      data: makeStory({ id: 'story-1', type: 'character_driven', scenes: [] }),
    })
    getCharacters.mockResolvedValue({
      data: [makeCharacter({ id: 'hero', name: 'Hero' })],
    })
    getModels.mockResolvedValue({
      data: makeModelRegistry({
        default_model_id: 'model-a',
        models: { 'model-a': makeModel({ name: 'Model A' }) },
      }),
    })
    render(<App />)

    expect(
      await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    ).toBeInTheDocument()
  })

  it('renders the character-scene placeholder', () => {
    window.history.replaceState({}, '', '/stories/story-1/character-scenes/scene-1')
    render(<App />)

    expect(screen.getByText('Character scene page is not available yet.')).toBeInTheDocument()
  })
})
