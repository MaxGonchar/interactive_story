import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  deleteCharacterSceneItem,
  editCharacterSceneItem,
  finishCharacterScene,
  getCharacterMemoryDraft,
  getCharacterScene,
  getCharacterSceneSummaryDraft,
  replaceCharacterTurn,
  submitCharacterTurn,
} from '../api/character_play'
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
        <Route path="/stories/:storyId" element={<p>Story page reached</p>} />
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
    expect(screen.queryByRole('button', { name: 'Edit paragraph' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()
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
    expect(screen.queryByRole('button', { name: 'Edit paragraph' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()
  })

  // --- paragraph actions ---

  it('edits any paragraph in place and keeps Delete off the opening item', async () => {
    const user = userEvent.setup()
    const opening = makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' })
    const last = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ items: [opening, last] }),
    })
    editCharacterSceneItem.mockResolvedValue({
      data: { ...last, narration: 'Updated last paragraph.' },
    })
    renderPage()
    await screen.findByText('Opening.')

    const articles = screen.getAllByRole('article')
    expect(within(articles[0]).getByRole('button', { name: 'Edit paragraph' })).toBeInTheDocument()
    expect(within(articles[0]).queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()
    expect(within(articles[1]).getByRole('button', { name: 'Delete paragraph' })).toBeInTheDocument()
    await user.click(within(articles[1]).getByRole('button', { name: 'Edit paragraph' }))
    await user.clear(screen.getByRole('textbox', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Updated last paragraph.')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(editCharacterSceneItem).toHaveBeenCalledWith(
      'story-1',
      'scene-1',
      'last',
      'Updated last paragraph.'
    )
    expect(await screen.findByText('Updated last paragraph.')).toBeInTheDocument()
    expect(screen.queryByText('Last.')).not.toBeInTheDocument()
  })

  it('keeps a failed edit draft open and displays its error', async () => {
    const user = userEvent.setup()
    const last = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ items: [makeCharacterSceneItem(), last] }),
    })
    editCharacterSceneItem.mockRejectedValue(new Error('Edit failed'))
    renderPage()
    await screen.findByText('Last.')

    const articles = screen.getAllByRole('article')
    await user.click(within(articles[1]).getByRole('button', { name: 'Edit paragraph' }))
    await user.clear(screen.getByRole('textbox', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Keep this draft.')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Edit failed')
    expect(screen.getByRole('textbox', { name: 'Edit paragraph' })).toHaveValue('Keep this draft.')
  })

  it('deletes the last paragraph after the API succeeds', async () => {
    const user = userEvent.setup()
    const opening = makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' })
    const last = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ items: [opening, last] }),
    })
    deleteCharacterSceneItem.mockResolvedValue({ data: { success: true } })
    renderPage()
    await screen.findByText('Last.')

    await user.click(screen.getByRole('button', { name: 'Delete paragraph' }))

    expect(deleteCharacterSceneItem).toHaveBeenCalledWith('story-1', 'scene-1', 'last')
    expect(await screen.findByText('Opening.')).toBeInTheDocument()
    expect(screen.queryByText('Last.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()
  })

  it('shows an error when deleting the last paragraph fails', async () => {
    const user = userEvent.setup()
    const last = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ items: [makeCharacterSceneItem(), last] }),
    })
    deleteCharacterSceneItem.mockRejectedValue(new Error('Delete failed'))
    renderPage()
    await screen.findByText('Last.')

    await user.click(screen.getByRole('button', { name: 'Delete paragraph' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Delete failed')
    expect(screen.getByText('Last.')).toBeInTheDocument()
  })

  // --- retry a turn ---

  it('stages the last player turn and restores the prior draft when canceled', async () => {
    const opening = makeCharacterSceneItem({
      id: 'opening',
      narration: 'Opening.',
      llm_data: { character_model_id: 'model-a', narrator_model_id: 'model-a' },
    })
    const last = makeCharacterSceneItem({
      id: 'last',
      actor: { type: 'player' },
      input: { action: 'Original action' },
      narration: 'Last.',
      llm_data: { character_model_id: null, narrator_model_id: 'model-b' },
    })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        user_character_id: 'hero',
        character_ids: ['guard'],
        items: [opening, last],
      }),
    })
    renderPage()
    await screen.findByText('Last.')

    await userEvent.selectOptions(screen.getByLabelText('Actor'), 'guard')
    await userEvent.type(screen.getByLabelText('Guidance'), 'Unsaved guidance')
    await userEvent.selectOptions(screen.getByLabelText('Character LLM'), 'model-b')
    await userEvent.selectOptions(screen.getByLabelText('LLM'), 'model-a')
    await userEvent.click(screen.getByRole('button', { name: 'Retry paragraph' }))

    expect(screen.getByLabelText('Actor')).toHaveValue('player')
    expect(screen.getByLabelText('Action')).toHaveValue('Original action')
    expect(screen.getByLabelText('Character LLM')).toHaveValue('model-b')
    expect(screen.getByLabelText('LLM')).toHaveValue('model-b')
    expect(screen.getAllByRole('button', { name: 'Edit paragraph' }).every((button) => button.disabled))
      .toBe(true)
    expect(screen.getByRole('button', { name: 'Delete paragraph' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Retry paragraph' })).toBeDisabled()

    await userEvent.click(screen.getByRole('button', { name: 'Cancel retry' }))

    expect(screen.getByLabelText('Actor')).toHaveValue('guard')
    expect(screen.getByLabelText('Guidance')).toHaveValue('Unsaved guidance')
    expect(screen.getByLabelText('Character LLM')).toHaveValue('model-b')
    expect(screen.getByLabelText('LLM')).toHaveValue('model-a')
    expect(screen.getByRole('button', { name: 'Trigger' })).toBeEnabled()
  })

  it('stages the last character turn, replaces it in place, and resets the composer', async () => {
    const opening = makeCharacterSceneItem({
      id: 'opening',
      narration: 'Opening.',
      llm_data: { character_model_id: 'model-a', narrator_model_id: 'model-a' },
    })
    const last = makeCharacterSceneItem({
      id: 'last',
      actor: { type: 'character', character_id: 'guard' },
      input: { guidance: 'Original guidance' },
      narration: 'Last.',
      llm_data: { character_model_id: 'model-b', narrator_model_id: 'model-a' },
    })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        user_character_id: 'hero',
        character_ids: ['guard'],
        items: [opening, last],
      }),
    })
    replaceCharacterTurn.mockResolvedValue({
      data: makeCharacterSceneItem({
        id: 'last',
        narration: 'Replacement.',
        llm_data: { character_model_id: 'model-a', narrator_model_id: 'model-b' },
      }),
    })
    renderPage()
    await screen.findByText('Last.')

    await userEvent.click(screen.getByRole('button', { name: 'Retry paragraph' }))

    expect(screen.getByLabelText('Actor')).toHaveValue('guard')
    expect(screen.getByLabelText('Guidance')).toHaveValue('Original guidance')
    expect(screen.getByLabelText('Character LLM')).toHaveValue('model-b')
    expect(screen.getByLabelText('LLM')).toHaveValue('model-a')

    await userEvent.clear(screen.getByLabelText('Guidance'))
    await userEvent.type(screen.getByLabelText('Guidance'), 'Changed guidance')
    await userEvent.selectOptions(screen.getByLabelText('Character LLM'), 'model-a')
    await userEvent.selectOptions(screen.getByLabelText('LLM'), 'model-b')
    await userEvent.click(screen.getByRole('button', { name: 'Replace last paragraph' }))

    expect(replaceCharacterTurn).toHaveBeenCalledWith('story-1', 'scene-1', 'last', {
      actor: { type: 'character', character_id: 'guard' },
      guidance: 'Changed guidance',
      character_model_id: 'model-a',
      narrator_model_id: 'model-b',
    })
    expect(submitCharacterTurn).not.toHaveBeenCalled()
    expect(await screen.findByText('Replacement.')).toBeInTheDocument()
    expect(screen.queryByText('Last.')).not.toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
    expect(screen.getByLabelText('Actor')).toHaveValue('player')
    expect(screen.getByLabelText('Action')).toHaveValue('')
    expect(screen.getByLabelText('LLM')).toHaveValue('model-b')
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('keeps retry mode and staged inputs when replacement fails', async () => {
    const last = makeCharacterSceneItem({
      id: 'last',
      actor: { type: 'player' },
      input: { action: 'Original action' },
      narration: 'Last.',
      llm_data: { character_model_id: null, narrator_model_id: 'model-b' },
    })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        items: [makeCharacterSceneItem({ id: 'opening' }), last],
      }),
    })
    replaceCharacterTurn.mockRejectedValue(new Error('Replacement failed'))
    renderPage()
    await screen.findByText('Last.')

    await userEvent.click(screen.getByRole('button', { name: 'Retry paragraph' }))
    await userEvent.clear(screen.getByLabelText('Action'))
    await userEvent.type(screen.getByLabelText('Action'), 'Adjusted action')
    await userEvent.click(screen.getByRole('button', { name: 'Replace last paragraph' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Replacement failed')
    expect(screen.getByRole('button', { name: 'Replace last paragraph' })).toBeEnabled()
    expect(screen.getByLabelText('Actor')).toHaveValue('player')
    expect(screen.getByLabelText('Action')).toHaveValue('Adjusted action')
    expect(screen.getByText('Last.')).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('returns to an empty Player composer when retry is canceled without a draft', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        items: [
          makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' }),
          makeCharacterSceneItem({
            id: 'last',
            actor: { type: 'player' },
            input: { action: 'Original action' },
            narration: 'Last.',
          }),
        ],
      }),
    })
    renderPage()
    await screen.findByText('Last.')

    await userEvent.click(screen.getByRole('button', { name: 'Retry paragraph' }))
    await userEvent.click(screen.getByRole('button', { name: 'Cancel retry' }))

    expect(screen.getByLabelText('Actor')).toHaveValue('player')
    expect(screen.getByLabelText('Action')).toHaveValue('')
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('hides the composer for a finished scene', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({ finished: true, items: [makeCharacterSceneItem()] }),
    })
    renderPage()

    await screen.findByText('This scene is finished.')
    expect(screen.queryByRole('group', { name: 'Turn composer' })).not.toBeInTheDocument()
  })

  it('generates and edits finish drafts, then finishes the scene and navigates to the story', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue({
      data: { summary: ['Generated summary'] },
    })
    getCharacterMemoryDraft.mockImplementation(async (_storyId, _sceneId, characterId) => ({
      data: { character_id: characterId, memory_updates: [`Memory for ${characterId}`] },
    }))
    finishCharacterScene.mockResolvedValue({ data: { finished: true } })
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('First.')

    await user.click(screen.getByRole('button', { name: 'Finish' }))

    const tabs = screen.getAllByRole('tab')
    expect(tabs.map((tab) => tab.textContent)).toEqual([
      'SummaryEmpty',
      'HeroEmpty',
      'Harbor GuardEmpty',
    ])
    expect(screen.getByRole('textbox', { name: 'Summary editor' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Generate all' }))
    expect(await screen.findByRole('tab', { name: /Harbor Guard.*Generated/ })).toBeInTheDocument()
    await user.clear(screen.getByRole('textbox', { name: 'Summary editor' }))
    await user.type(screen.getByRole('textbox', { name: 'Summary editor' }), 'Reviewed summary')
    await user.click(screen.getByRole('tab', { name: /Hero/ }))
    await user.clear(screen.getByRole('textbox', { name: 'Hero editor' }))
    await user.type(screen.getByRole('textbox', { name: 'Hero editor' }), 'Edited hero memory')
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(finishCharacterScene).toHaveBeenCalledWith(
      'story-1',
      'scene-1',
      ['Reviewed summary'],
      {
        hero: ['Edited hero memory'],
        guard: ['Memory for guard'],
      }
    )
    expect(await screen.findByText('Story page reached')).toBeInTheDocument()
  })

  it('keeps the finish modal open and shows an inline error when finishing fails', async () => {
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        user_character_id: null,
        character_ids: [],
        items: [makeCharacterSceneItem({ narration: 'Opening.' })],
      }),
    })
    finishCharacterScene.mockRejectedValue(new Error('Finish failed'))
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Opening.')

    await user.click(screen.getByRole('button', { name: 'Finish' }))
    await user.type(screen.getByRole('textbox', { name: 'Summary editor' }), 'Reviewed summary')
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Finish failed')
    expect(screen.getByRole('textbox', { name: 'Summary editor' })).toHaveValue(
      '- Reviewed summary'
    )
    expect(screen.getByRole('button', { name: 'Finish scene' })).toBeInTheDocument()
    expect(finishCharacterScene).toHaveBeenCalledWith(
      'story-1',
      'scene-1',
      ['Reviewed summary'],
      {}
    )
  })
})
