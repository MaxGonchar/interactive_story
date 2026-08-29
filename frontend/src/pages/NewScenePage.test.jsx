import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import NewScenePage from './NewScenePage'
import { getStory } from '../api/stories'
import { getScene, createScene } from '../api/scenes'
import { getCharacters } from '../api/characters'
import { makeCharacter, makeScene, makeStory } from '../tests/factories'

vi.mock('../api/stories')
vi.mock('../api/scenes')
vi.mock('../api/characters')

const storyId = 'story-1'

function renderPage() {
  return render(
    <MemoryRouter initialEntries={[`/stories/${storyId}/scenes/new`]}>
      <Routes>
        <Route path="/stories/:storyId/scenes/new" element={<NewScenePage />} />
        <Route path="/stories/:storyId/scenes/:sceneId" element={<p>Created</p>} />
      </Routes>
    </MemoryRouter>
  )
}

async function completeForm() {
  await userEvent.clear(screen.getByLabelText('Context'))
  await userEvent.type(screen.getByLabelText('Context'), 'The party reaches the manor')
  await userEvent.type(screen.getByLabelText('General scene guide'), 'Reveal a clue.')
  await userEvent.clear(screen.getByLabelText('Writing style'))
  await userEvent.type(screen.getByLabelText('Writing style'), 'Atmospheric prose.')
  await userEvent.type(screen.getByLabelText('First message'), 'Rain lashes the windows.')
}

describe('NewScenePage', () => {
  let characters

  beforeEach(() => {
    vi.resetAllMocks()
    characters = [
      makeCharacter({ id: 'hero', name: 'Hero' }),
      makeCharacter({ id: 'villain', name: 'Villain' }),
    ]
    const previousScene = makeScene({ id: 1, finished: true })
    getStory.mockResolvedValue({ data: makeStory({ scenes: [previousScene] }) })
    getCharacters.mockResolvedValue({ data: characters })
    getScene.mockResolvedValue({
      data: makeScene({
        context: ['The storm is building'],
        scene_summary: ['The party has arrived'],
        scene_description: { writing_style: 'Atmospheric prose.' },
        messages: [],
      }),
    })
  })

  it('renders separate placeholder and Narrator options', async () => {
    renderPage()

    expect(await screen.findByRole('option', { name: '— select —' })).toHaveValue('')
    expect(screen.getByRole('option', { name: 'Narrator' })).not.toHaveValue('')
  })

  it('shows a validation error only when no user role is selected', async () => {
    renderPage()

    await screen.findByRole('option', { name: 'Narrator' })
    await userEvent.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(screen.getByText('User character is required')).toBeInTheDocument()
  })

  it('keeps every character eligible as a scene character in narrator mode', async () => {
    renderPage()

    await screen.findByRole('option', { name: 'Narrator' })
    await userEvent.selectOptions(screen.getByLabelText('User character'), 'Narrator')

    const heroCheckbox = screen.getByRole('checkbox', { name: 'Hero' })
    const villainCheckbox = screen.getByRole('checkbox', { name: 'Villain' })
    expect(heroCheckbox).toBeEnabled()
    expect(villainCheckbox).toBeEnabled()

    await userEvent.click(heroCheckbox)
    expect(heroCheckbox).toBeChecked()
  })

  it('excludes a selected user character from scene characters', async () => {
    renderPage()

    await screen.findByRole('option', { name: 'Narrator' })
    const heroCheckbox = screen.getByRole('checkbox', { name: 'Hero' })
    await userEvent.click(heroCheckbox)
    await userEvent.selectOptions(screen.getByLabelText('User character'), 'Hero')

    expect(heroCheckbox).toBeDisabled()
    expect(heroCheckbox).not.toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Villain' })).toBeEnabled()
  })

  it('submits narrator mode with a null user character ID and all form data', async () => {
    createScene.mockResolvedValue({ data: { id: 2 } })
    renderPage()

    await screen.findByRole('option', { name: 'Narrator' })
    await userEvent.selectOptions(screen.getByLabelText('User character'), 'Narrator')
    await userEvent.click(screen.getByRole('checkbox', { name: 'Hero' }))
    await userEvent.click(screen.getByRole('checkbox', { name: 'Villain' }))
    await completeForm()
    await userEvent.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(createScene).toHaveBeenCalledWith(storyId, {
      user_character_id: null,
      character_ids: ['hero', 'villain'],
      context: ['The party reaches the manor'],
      general_scene_guide: 'Reveal a clue.',
      writing_style: 'Atmospheric prose.',
      first_message: 'Rain lashes the windows.',
    })
    expect(await screen.findByText('Created')).toBeInTheDocument()
  })

  it('submits the selected character ID in character mode', async () => {
    createScene.mockResolvedValue({ data: { id: 2 } })
    renderPage()

    await screen.findByRole('option', { name: 'Narrator' })
    await userEvent.selectOptions(screen.getByLabelText('User character'), 'Hero')
    await completeForm()
    await userEvent.click(screen.getByRole('button', { name: 'Create scene' }))

    expect(createScene).toHaveBeenCalledWith(storyId, {
      user_character_id: 'hero',
      character_ids: [],
      context: ['The party reaches the manor'],
      general_scene_guide: 'Reveal a clue.',
      writing_style: 'Atmospheric prose.',
      first_message: 'Rain lashes the windows.',
    })
  })
})