import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import StoryPage from './StoryPage'
import { getStory } from '../api/stories'
import { makeStory, makeScene } from '../tests/factories'

vi.mock('../api/stories')

function renderPage(storyId = 'story-1') {
  return render(
    <MemoryRouter initialEntries={[`/stories/${storyId}`]}>
      <Routes>
        <Route path="/stories/:storyId" element={<StoryPage />} />
      </Routes>
    </MemoryRouter>
  )
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

  it('renders error message on API failure', async () => {
    getStory.mockRejectedValue(new Error('Failed to load story'))
    renderPage()
    expect(await screen.findByText('Failed to load story')).toBeInTheDocument()
  })
})
