import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ScenePage from './ScenePage'
import { getScene } from '../api/scenes'
import { makeScene, makeMessage } from '../tests/factories'

vi.mock('../api/scenes')

function renderPage(storyId = 'story-1', sceneId = 'scene-1') {
  return render(
    <MemoryRouter initialEntries={[`/stories/${storyId}/scenes/${sceneId}`]}>
      <Routes>
        <Route path="/stories/:storyId/scenes/:sceneId" element={<ScenePage />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('ScenePage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading state', () => {
    getScene.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders message list on success', async () => {
    const message = makeMessage({ role: 'user', content: 'Once upon a time' })
    const scene = makeScene({ messages: [message] })
    getScene.mockResolvedValue({ data: scene })
    renderPage()
    expect(await screen.findByText('Once upon a time')).toBeInTheDocument()
  })

  it('renders error message on API failure', async () => {
    getScene.mockRejectedValue(new Error('Failed to load scene'))
    renderPage()
    expect(await screen.findByText('Failed to load scene')).toBeInTheDocument()
  })
})
