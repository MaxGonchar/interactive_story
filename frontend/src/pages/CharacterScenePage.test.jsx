import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getCharacterScene, submitCharacterTurn } from '../api/character_play'
import { getCharacters } from '../api/characters'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import {
  makeCharacter,
  makeCharacterScene,
  makeCharacterSceneItem,
  makeModel,
  makeModelRegistry,
  makeStory,
} from '../tests/factories'
import CharacterScenePage from './CharacterScenePage'

vi.mock('../api/character_play')
vi.mock('../api/characters')
vi.mock('../api/models')
vi.mock('../api/stories')

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/stories/story-1/character-scenes/scene-1']}>
      <Routes>
        <Route
          path="/stories/:storyId/character-scenes/:sceneId"
          element={<CharacterScenePage />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe('CharacterScenePage', () => {
  const scrollIntoView = vi.fn()

  beforeEach(() => {
    vi.resetAllMocks()
    Element.prototype.scrollIntoView = scrollIntoView
    getStory.mockResolvedValue({ data: makeStory({ id: 'story-1', title: 'Harbor Tale' }) })
    getCharacters.mockResolvedValue({
      data: [
        makeCharacter({ id: 'hero', name: 'Hero' }),
        makeCharacter({ id: 'guard', name: 'Harbor Guard' }),
      ],
    })
    getModels.mockResolvedValue({
      data: makeModelRegistry({
        default_model_id: 'model-a',
        models: {
          'model-a': makeModel({ name: 'Model A' }),
          'model-b': makeModel({ name: 'Model B' }),
        },
      }),
    })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        id: 'scene-1',
        user_character_id: 'hero',
        character_ids: ['guard'],
        items: [
          makeCharacterSceneItem({
            narration: 'First.',
            llm_data: { character_model_id: null, narrator_model_id: 'model-b' },
          }),
          makeCharacterSceneItem({
            narration: 'Second.',
            llm_data: { character_model_id: null, narrator_model_id: 'model-b' },
          }),
        ],
      }),
    })
  })

  afterEach(cleanup)

  it('renders the header, ordered items and character names', async () => {
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Scene scene-1' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Harbor Tale' })).toBeInTheDocument()
    expect(screen.getAllByRole('article').map((el) => el.textContent)).toEqual([
      'First.',
      'Second.',
    ])
    expect(screen.getByText('Player: Hero')).toBeInTheDocument()
    expect(screen.getByText('Characters: Harbor Guard')).toBeInTheDocument()
    expect(getCharacterScene).toHaveBeenCalledWith('story-1', 'scene-1')
  })

  it('shows the narrator model derived from the items under the LLM label', async () => {
    renderPage()

    expect(await screen.findByLabelText('LLM')).toHaveValue('model-b')
  })

  it('labels a null player as Narrator', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ user_character_id: null, character_ids: [], items: [] }),
    })

    renderPage()

    expect(await screen.findByText('Player: Narrator')).toBeInTheDocument()
    expect(screen.queryByText(/Characters:/)).not.toBeInTheDocument()
  })

  it('shows the finished state', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ finished: true, items: [makeCharacterSceneItem()] }),
    })

    renderPage()

    expect(await screen.findByText('This scene is finished.')).toBeInTheDocument()
    expect(screen.getByLabelText('LLM')).toBeDisabled()
  })

  it('does not show the finished state for an active scene', async () => {
    renderPage()

    await screen.findByText('First.')
    expect(screen.queryByText('This scene is finished.')).not.toBeInTheDocument()
  })

  it('shows a loading state', () => {
    getCharacterScene.mockReturnValue(new Promise(() => {}))

    renderPage()

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('shows an error when loading fails', async () => {
    getCharacterScene.mockRejectedValue(new Error('Scene not found'))

    renderPage()

    expect(await screen.findByText('Scene not found')).toBeInTheDocument()
  })

  it('scrolls to the end once after loading', async () => {
    renderPage()

    await screen.findByText('First.')

    expect(scrollIntoView).toHaveBeenCalledTimes(1)
  })

  // --- send a turn ---

  it('sends a player turn, appends the item and resets the composer', async () => {
    submitCharacterTurn.mockResolvedValue({
      data: makeCharacterSceneItem({
        narration: 'Light appears.',
        llm_data: { character_model_id: null, narrator_model_id: 'model-a' },
      }),
    })
    renderPage()
    await screen.findByText('First.')

    await userEvent.type(screen.getByLabelText('Action'), 'Look for light')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Light appears.')).toBeInTheDocument()
    expect(submitCharacterTurn).toHaveBeenCalledWith('story-1', 'scene-1', {
      actor: { type: 'player' },
      action: 'Look for light',
      character_model_id: 'model-a',
      narrator_model_id: 'model-b',
    })
    expect(screen.getByLabelText('Action')).toHaveValue('')
    expect(screen.getByLabelText('LLM')).toHaveValue('model-a')
  })

  it('blocks a player turn with empty text', async () => {
    renderPage()
    await screen.findByText('First.')

    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('triggers a character with empty guidance, then resets the actor to Player', async () => {
    submitCharacterTurn.mockResolvedValue({
      data: makeCharacterSceneItem({
        narration: 'The guard speaks.',
        llm_data: { character_model_id: 'model-b', narrator_model_id: 'model-b' },
      }),
    })
    renderPage()
    await screen.findByText('First.')

    await userEvent.selectOptions(screen.getByLabelText('Actor'), 'guard')
    await userEvent.selectOptions(screen.getByLabelText('Character LLM'), 'model-a')
    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    expect(await screen.findByText('The guard speaks.')).toBeInTheDocument()
    expect(submitCharacterTurn).toHaveBeenCalledWith('story-1', 'scene-1', {
      actor: { type: 'character', character_id: 'guard' },
      guidance: '',
      character_model_id: 'model-a',
      narrator_model_id: 'model-b',
    })
    expect(screen.getByLabelText('Actor')).toHaveValue('player')
    expect(screen.getByLabelText('Character LLM')).toHaveValue('model-b')
  })

  it('keeps the inputs and shows an error when the turn fails', async () => {
    submitCharacterTurn.mockRejectedValue(new Error('LLM failed'))
    renderPage()
    await screen.findByText('First.')

    await userEvent.type(screen.getByLabelText('Action'), 'Look')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('LLM failed')
    expect(screen.getByLabelText('Action')).toHaveValue('Look')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Send' })).toBeEnabled())
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('shows the progress label for the selected actor type while sending', async () => {
    submitCharacterTurn.mockReturnValue(new Promise(() => {}))
    renderPage()
    await screen.findByText('First.')

    await userEvent.type(screen.getByLabelText('Action'), 'Look')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(screen.getByText('Narrator is writing')).toBeInTheDocument()
  })

  it('hides the composer for a finished scene', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ finished: true, items: [makeCharacterSceneItem()] }),
    })
    renderPage()

    await screen.findByText('This scene is finished.')
    expect(screen.queryByRole('group', { name: 'Turn composer' })).not.toBeInTheDocument()
  })
})
