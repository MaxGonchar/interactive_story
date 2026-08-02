import React from 'react'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ScenePage from './ScenePage'
import { getScene, playScene } from '../api/scenes'
import { makeScene, makeMessage } from '../tests/factories'

vi.mock('../api/scenes')

const scrollIntoViewMock = vi.fn()

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
    Object.defineProperty(window.HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollIntoViewMock,
    })
  })

  afterEach(() => {
    scrollIntoViewMock.mockReset()
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

  it('renders dedicated message and composer regions on success', async () => {
    const message = makeMessage({ role: 'user', content: 'Once upon a time' })
    const scene = makeScene({ messages: [message] })
    getScene.mockResolvedValue({ data: scene })

    renderPage()

    expect(await screen.findByRole('log', { name: 'Scene messages' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Scene composer area' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Message composer' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Finish' })).toBeInTheDocument()

    const actions = screen.getByRole('group', { name: 'Message composer actions' })
    expect(within(actions).getByRole('button', { name: 'Finish' })).toBeInTheDocument()
    expect(within(actions).getByRole('button', { name: 'Send' })).toBeInTheDocument()
  })

  it('renders error message on API failure', async () => {
    getScene.mockRejectedValue(new Error('Failed to load scene'))
    renderPage()
    expect(await screen.findByText('Failed to load scene')).toBeInTheDocument()
  })

  it('scrolls to the newest message after a send appends the response pair', async () => {
    const initialScene = makeScene({
      messages: [makeMessage({ role: 'user', content: 'Before the turn' })],
    })
    const userMessage = makeMessage({ role: 'user', content: 'I open the door' })
    const assistantMessage = makeMessage({ role: 'assistant', content: 'The hinges groan open.' })

    getScene.mockResolvedValue({ data: initialScene })
    playScene.mockResolvedValue({
      data: {
        user_message: userMessage,
        assistant_message: assistantMessage,
      },
    })

    renderPage()

    await screen.findByText('Before the turn')
    scrollIntoViewMock.mockClear()

    await userEvent.type(screen.getByRole('textbox'), 'I open the door')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('The hinges groan open.')).toBeInTheDocument()
    expect(playScene).toHaveBeenCalledWith('story-1', 'scene-1', 'I open the door')
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ block: 'end' })
    expect(screen.getByRole('group', { name: 'Message composer' })).toBeInTheDocument()
  })
})
