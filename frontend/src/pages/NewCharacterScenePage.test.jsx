import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getCharacters } from '../api/characters'
import { createCharacterScene, getCharacterScene } from '../api/character_play'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import {
  makeCharacter,
  makeCharacterScene,
  makeCharacterSceneItem,
  makeModel,
  makeModelRegistry,
  makeScene,
  makeStory,
} from '../tests/factories'
import NewCharacterScenePage from './NewCharacterScenePage'

vi.mock('../api/characters')
vi.mock('../api/character_play')
vi.mock('../api/models')
vi.mock('../api/stories')

const storyId = 'story-1'

function makeRegistry() {
  return makeModelRegistry({
    default_model_id: 'model-a',
    models: {
      'model-a': makeModel({ name: 'Model A' }),
      'model-b': makeModel({ name: 'Model B' }),
    },
  })
}

function renderPage() {
  return render(
    <MemoryRouter initialEntries={[`/stories/${storyId}/character-scenes/new`]}>
      <Routes>
        <Route
          path="/stories/:storyId/character-scenes/new"
          element={<NewCharacterScenePage />}
        />
        <Route
          path="/stories/:storyId/character-scenes/:sceneId"
          element={<p>Created scene</p>}
        />
      </Routes>
    </MemoryRouter>
  )
}

async function fillForm(user, { player = 'Narrator' } = {}) {
  await user.selectOptions(screen.getByLabelText('Player'), player)
  await user.type(screen.getByLabelText('Context'), 'The party reaches the harbor.')
  await user.type(screen.getByLabelText('General scene guide'), 'Raise the tension.')
  await user.type(screen.getByLabelText('Writing style'), 'Cinematic prose.')
  await user.type(
    screen.getByLabelText('Opening narrator paragraph'),
    'A bell rings through the fog.'
  )
}

describe('NewCharacterScenePage', () => {
  const characters = [
    makeCharacter({ id: 'hero', name: 'Hero' }),
    makeCharacter({ id: 'navigator', name: 'Navigator' }),
  ]

  beforeEach(() => {
    vi.resetAllMocks()
    getStory.mockResolvedValue({
      data: makeStory({ id: storyId, type: 'character_driven', scenes: [] }),
    })
    getCharacters.mockResolvedValue({ data: characters })
    getModels.mockResolvedValue({ data: makeRegistry() })
    getCharacterScene.mockResolvedValue({ data: makeCharacterScene() })
  })

  it('loads the shared data and renders the four form sections', async () => {
    renderPage()

    expect(
      await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    ).toBeInTheDocument()
    expect(getStory).toHaveBeenCalledWith(storyId)
    expect(getCharacters).toHaveBeenCalledWith(storyId)
    expect(getModels).toHaveBeenCalled()
    expect(screen.getByRole('group', { name: 'Participants' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Starting situation' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Narrative direction' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Agents' })).toBeInTheDocument()
    expect(screen.getByRole('combobox', { name: 'Character agent model' })).toHaveValue(
      'model-a'
    )
    expect(screen.getByRole('combobox', { name: 'Narrator agent model' })).toHaveValue(
      'model-a'
    )
  })

  it('prefills values and models from the last finished scene only', async () => {
    getStory.mockResolvedValue({
      data: makeStory({
        id: storyId,
        type: 'character_driven',
        scenes: [
          makeScene({ id: 8, finished: true }),
          makeScene({ id: 9, finished: false }),
          makeScene({ id: 10, finished: true }),
        ],
      }),
    })
    getCharacterScene.mockResolvedValue({
      data: makeCharacterScene({
        context: ['The ship reaches the harbor.'],
        scene_summary: ['The crew found a hidden signal.'],
        scene_description: {
          general_scene_guide: 'This should not be copied.',
          writing_style: 'Cinematic prose.',
        },
        items: [
          makeCharacterSceneItem({
            narration: 'The fog gathers.',
            llm_data: {
              character_model_id: 'model-b',
              narrator_model_id: 'model-b',
            },
          }),
          makeCharacterSceneItem({
            narration: 'A bell rings through the fog.',
            llm_data: {
              character_model_id: null,
              narrator_model_id: 'removed-model',
            },
          }),
        ],
      }),
    })

    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })

    expect(getCharacterScene).toHaveBeenCalledWith(storyId, 10)
    expect(screen.getByLabelText('Context')).toHaveValue(
      '- The ship reaches the harbor.\n- The crew found a hidden signal.'
    )
    expect(screen.getByLabelText('Writing style')).toHaveValue('Cinematic prose.')
    expect(screen.getByLabelText('Opening narrator paragraph')).toHaveValue(
      'A bell rings through the fog.'
    )
    expect(screen.getByLabelText('General scene guide')).toHaveValue('')
    expect(screen.getByLabelText('Character agent model')).toHaveValue('model-b')
    expect(screen.getByLabelText('Narrator agent model')).toHaveValue('model-a')
  })

  it('keeps the player character out of the NPC selection', async () => {
    const user = userEvent.setup()
    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    const heroCheckbox = screen.getByRole('checkbox', { name: 'Hero' })
    await user.click(heroCheckbox)
    await user.selectOptions(screen.getByLabelText('Player'), 'Hero')

    expect(heroCheckbox).toBeDisabled()
    expect(heroCheckbox).not.toBeChecked()

    await user.click(screen.getByRole('checkbox', { name: 'Navigator' }))
    await user.selectOptions(screen.getByLabelText('Player'), 'Navigator')

    expect(screen.getByRole('checkbox', { name: 'Navigator' })).not.toBeChecked()
  })

  it('shows validation messages and blocks submission for required fields', async () => {
    const user = userEvent.setup()
    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    await user.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(screen.getByText('Player is required')).toBeInTheDocument()
    expect(screen.getByText('At least one context bullet is required')).toBeInTheDocument()
    expect(screen.getByText('General scene guide is required')).toBeInTheDocument()
    expect(screen.getByText('Writing style is required')).toBeInTheDocument()
    expect(screen.getByText('Opening narrator paragraph is required')).toBeInTheDocument()
    expect(createCharacterScene).not.toHaveBeenCalled()
  })

  it('rejects an opening narrator paragraph longer than 4000 characters', async () => {
    const user = userEvent.setup()
    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    await fillForm(user)
    fireEvent.change(screen.getByLabelText('Opening narrator paragraph'), {
      target: { value: 'x'.repeat(4001) },
    })
    await user.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(
      screen.getByText('Opening narrator paragraph must be 4000 characters or fewer')
    ).toBeInTheDocument()
    expect(createCharacterScene).not.toHaveBeenCalled()
  })

  it('submits the documented payload and navigates to the created scene', async () => {
    const user = userEvent.setup()
    createCharacterScene.mockResolvedValue({ data: { id: 42 } })
    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    await user.selectOptions(screen.getByLabelText('Player'), 'Hero')
    await user.click(screen.getByRole('checkbox', { name: 'Navigator' }))
    await user.type(screen.getByLabelText('Context'), 'The party reaches the harbor.')
    await user.type(screen.getByLabelText('General scene guide'), 'Raise the tension.')
    await user.type(screen.getByLabelText('Writing style'), 'Cinematic prose.')
    await user.type(
      screen.getByLabelText('Opening narrator paragraph'),
      'A bell rings through the fog.'
    )
    await user.selectOptions(screen.getByLabelText('Character agent model'), 'model-b')
    await user.selectOptions(screen.getByLabelText('Narrator agent model'), 'model-b')
    await user.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(createCharacterScene).toHaveBeenCalledWith(storyId, {
      user_character_id: 'hero',
      character_ids: ['navigator'],
      context: ['The party reaches the harbor.'],
      general_scene_guide: 'Raise the tension.',
      writing_style: 'Cinematic prose.',
      first_message: 'A bell rings through the fog.',
      character_model_id: 'model-b',
      narrator_model_id: 'model-b',
    })
    expect(await screen.findByText('Created scene')).toBeInTheDocument()
  })

  it('shows a server conflict as the submit error', async () => {
    const user = userEvent.setup()
    createCharacterScene.mockRejectedValue(
      new Error('An active scene already exists (409 active_scene_exists)')
    )
    renderPage()

    await screen.findByRole('heading', { name: 'New Character-Driven Scene' })
    await fillForm(user)
    await user.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(
      await screen.findByText('An active scene already exists (409 active_scene_exists)')
    ).toBeInTheDocument()
  })

  it('shows a loading error when page data cannot be loaded', async () => {
    getModels.mockRejectedValue(new Error('Model registry unavailable'))
    renderPage()

    expect(await screen.findByText('Model registry unavailable')).toBeInTheDocument()
  })
})
