import { act, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ScenePage from './ScenePage'
import { getScene, playScene, regenerateLastAssistantMessage } from '../api/scenes'
import { getModels } from '../api/models'
import { makeScene, makeMessage, makeModel, makeModelRegistry } from '../tests/factories'

vi.mock('../api/scenes')
vi.mock('../api/models')

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
    getModels.mockResolvedValue({ data: makeModelRegistry() })
    Object.defineProperty(window.HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollIntoViewMock,
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    scrollIntoViewMock.mockReset()
  })

  it('renders loading state', () => {
    getScene.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('keeps loading until the model registry is available', () => {
    getScene.mockResolvedValue({ data: makeScene() })
    getModels.mockReturnValue(new Promise(() => {}))

    renderPage()

    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(getModels).toHaveBeenCalledTimes(1)
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

  it('renders an error message when the model registry cannot load', async () => {
    getScene.mockResolvedValue({ data: makeScene() })
    getModels.mockRejectedValue(new Error('Failed to load models'))

    renderPage()

    expect(await screen.findByText('Failed to load models')).toBeInTheDocument()
  })

  it('selects the registry default model for an empty scene', async () => {
    const defaultModel = makeModel({ id: 'default-model', name: 'Default Model' })
    const registry = makeModelRegistry({
      models: { [defaultModel.id]: defaultModel },
      default_model_id: defaultModel.id,
    })
    getScene.mockResolvedValue({ data: makeScene() })
    getModels.mockResolvedValue({ data: registry })

    renderPage()

    expect(await screen.findByRole('combobox', { name: 'Model' })).toHaveValue(defaultModel.id)
  })

  it('selects the latest assistant model from scene history', async () => {
    const defaultModel = makeModel({ id: 'default-model', name: 'Default Model' })
    const historicalModel = makeModel({ id: 'historical-model', name: 'Historical Model' })
    const registry = makeModelRegistry({
      models: {
        [defaultModel.id]: defaultModel,
        [historicalModel.id]: historicalModel,
      },
      default_model_id: defaultModel.id,
    })
    const scene = makeScene({
      messages: [
        makeMessage({ role: 'assistant', llm_data: { model_id: defaultModel.id } }),
        makeMessage({ role: 'user' }),
        makeMessage({ role: 'assistant', llm_data: { model_id: historicalModel.id } }),
      ],
    })
    getScene.mockResolvedValue({ data: scene })
    getModels.mockResolvedValue({ data: registry })

    renderPage()

    expect(await screen.findByRole('combobox', { name: 'Model' })).toHaveValue(historicalModel.id)
  })

  it('scrolls to the newest message after a send appends the response pair', async () => {
    const initialScene = makeScene({
      messages: [makeMessage({ role: 'user', content: 'Before the turn' })],
    })
    const userMessage = makeMessage({ role: 'user', content: 'I open the door' })
    const assistantMessage = makeMessage({
      role: 'assistant',
      content: 'The hinges groan open.',
      llm_data: { model_id: 'returned-model' },
    })
    const selectedModel = makeModel({ id: 'selected-model', name: 'Selected Model' })
    const returnedModel = makeModel({ id: 'returned-model', name: 'Returned Model' })

    getScene.mockResolvedValue({ data: initialScene })
    getModels.mockResolvedValue({
      data: makeModelRegistry({
        models: {
          [selectedModel.id]: selectedModel,
          [returnedModel.id]: returnedModel,
        },
        default_model_id: selectedModel.id,
      }),
    })
    playScene.mockResolvedValue({
      data: {
        user_message: userMessage,
        assistant_message: assistantMessage,
      },
    })

    renderPage()

    await screen.findByText('Before the turn')
    scrollIntoViewMock.mockClear()

    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Model' }), selectedModel.id)
    await userEvent.type(screen.getByRole('textbox'), 'I open the door')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('The hinges groan open.')).toBeInTheDocument()
    expect(playScene).toHaveBeenCalledWith('story-1', 'scene-1', 'I open the door', selectedModel.id)
    expect(screen.getByRole('combobox', { name: 'Model' })).toHaveValue(returnedModel.id)
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ block: 'end' })
    expect(screen.getByRole('group', { name: 'Message composer' })).toBeInTheDocument()
  })

  it('disables the model selector when the scene is finished', async () => {
    getScene.mockResolvedValue({ data: makeScene({ finished: true }) })

    renderPage()

    expect(await screen.findByRole('combobox', { name: 'Model' })).toBeDisabled()
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('tracks sending time while pending and hides it after success', async () => {
    let resolvePlay
    playScene.mockImplementation(() => new Promise((resolve) => { resolvePlay = resolve }))
    getScene.mockResolvedValue({ data: makeScene() })
    renderPage()

    await screen.findByRole('combobox', { name: 'Model' })
    vi.useFakeTimers()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'A new turn' } })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(screen.getByLabelText('Sending elapsed time')).toBeInTheDocument()
    act(() => {
      vi.advanceTimersByTime(12340)
    })
    expect(screen.getByText('00:12:340')).toBeInTheDocument()

    await act(async () => {
      resolvePlay({
        data: {
          user_message: makeMessage({ role: 'user', content: 'A new turn' }),
          assistant_message: makeMessage({ role: 'assistant', content: 'The answer.', llm_data: { model_id: 'model-1' } }),
        },
      })
      await Promise.resolve()
    })

    expect(screen.queryByLabelText('Sending elapsed time')).not.toBeInTheDocument()
  })

  it('hides sending time and preserves the error when sending fails', async () => {
    let rejectPlay
    playScene.mockImplementation(() => new Promise((resolve, reject) => { rejectPlay = reject }))
    getScene.mockResolvedValue({ data: makeScene() })
    renderPage()

    await screen.findByRole('combobox', { name: 'Model' })
    vi.useFakeTimers()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Try again' } })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await act(async () => {
      rejectPlay(new Error('Send failed'))
    })

    expect(screen.getByText('Send failed')).toBeInTheDocument()
    expect(screen.queryByLabelText('Sending elapsed time')).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('Try again')
  })

  it('tracks regeneration time while pending and hides it after success', async () => {
    let resolveRegenerate
    const assistantMessage = makeMessage({ role: 'assistant', content: 'Before regeneration' })
    getScene.mockResolvedValue({
      data: makeScene({ messages: [makeMessage({ role: 'user' }), assistantMessage] }),
    })
    regenerateLastAssistantMessage.mockImplementation(
      () => new Promise((resolve) => { resolveRegenerate = resolve })
    )
    renderPage()

    await screen.findByText('Before regeneration')
    vi.useFakeTimers()
    fireEvent.click(screen.getByLabelText('Regenerate message'))

    expect(screen.getByLabelText('Regenerating elapsed time')).toBeInTheDocument()
    act(() => {
      vi.advanceTimersByTime(10010)
    })
    expect(screen.getByText('00:10:010')).toBeInTheDocument()

    await act(async () => {
      resolveRegenerate({
        data: {
          assistant_message: { ...assistantMessage, content: 'After regeneration' },
        },
      })
    })

    expect(screen.getByText('After regeneration')).toBeInTheDocument()
    expect(screen.queryByLabelText('Regenerating elapsed time')).not.toBeInTheDocument()
  })

  it('hides regeneration time and preserves the error when regeneration fails', async () => {
    let rejectRegenerate
    getScene.mockResolvedValue({
      data: makeScene({ messages: [makeMessage({ role: 'user' }), makeMessage({ role: 'assistant' })] }),
    })
    regenerateLastAssistantMessage.mockImplementation(
      () => new Promise((resolve, reject) => { rejectRegenerate = reject })
    )
    renderPage()

    await screen.findByLabelText('Regenerate message')
    vi.useFakeTimers()
    fireEvent.click(screen.getByLabelText('Regenerate message'))

    await act(async () => {
      rejectRegenerate(new Error('Regeneration failed'))
    })

    expect(screen.getByText('Regeneration failed')).toBeInTheDocument()
    expect(screen.queryByLabelText('Regenerating elapsed time')).not.toBeInTheDocument()
  })
})
