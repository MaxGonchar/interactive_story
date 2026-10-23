import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import StoryPage from './StoryPage'
import { getStory } from '../api/stories'
import { makeStory, makeScene } from '../tests/factories'

vi.mock('../api/stories')

function renderPage(storyId = 'story-1') {
  return render(
    <MemoryRouter initialEntries={[`/stories/${storyId}`]}>
      <LocationDisplay />
      <Routes>
        <Route path="/stories/:storyId/*" element={<StoryPage />} />
      </Routes>
    </MemoryRouter>
  )
}

function LocationDisplay() {
  const { pathname } = useLocation()
  return <p>{pathname}</p>
}

describe('StoryPage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading state', () => {
    getStory.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders scene list on success', async () => {
    const scene = makeScene({ name: 'Opening Scene' })
    const story = makeStory({ title: 'Epic Tale', active_scene_id: null, scenes: [scene] })
    getStory.mockResolvedValue({ data: story })
    renderPage()
    expect(await screen.findByText('Epic Tale')).toBeInTheDocument()
  })

  it('navigates to character-scene routes for a character-driven story', async () => {
    const scene = makeScene({ id: 'scene-1' })
    const story = makeStory({
      type: 'character_driven',
      active_scene_id: null,
      scenes: [scene],
    })
    getStory.mockResolvedValue({ data: story })
    renderPage()

    await userEvent.click(await screen.findByText('Scene scene-1'))
    expect(screen.getByText('/stories/story-1/character-scenes/scene-1')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Create new scene' }))
    expect(screen.getByText('/stories/story-1/character-scenes/new')).toBeInTheDocument()
  })

  it('keeps scene routes for a scene-driven story', async () => {
    const scene = makeScene({ id: 'scene-2' })
    const story = makeStory({
      type: 'scene',
      active_scene_id: null,
      scenes: [scene],
    })
    getStory.mockResolvedValue({ data: story })
    renderPage()

    await userEvent.click(await screen.findByText('Scene scene-2'))
    expect(screen.getByText('/stories/story-1/scenes/scene-2')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Create new scene' }))
    expect(screen.getByText('/stories/story-1/scenes/new')).toBeInTheDocument()
  })

  it('renders error message on API failure', async () => {
    getStory.mockRejectedValue(new Error('Failed to load story'))
    renderPage()
    expect(await screen.findByText('Failed to load story')).toBeInTheDocument()
  })
})
