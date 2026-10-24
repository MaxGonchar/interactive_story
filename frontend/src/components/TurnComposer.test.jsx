import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import TurnComposer from './TurnComposer'

const models = [
  { id: 'model-a', name: 'Model A' },
  { id: 'model-b', name: 'Model B' },
]

function renderComposer(props = {}) {
  const handlers = {
    onActorChange: vi.fn(),
    onTextChange: vi.fn(),
    onCharacterModelChange: vi.fn(),
    onSubmit: vi.fn(),
  }
  render(
    <TurnComposer
      actor="player"
      characters={[{ id: 'guard', name: 'Harbor Guard' }]}
      text=""
      models={models}
      characterModelId="model-a"
      {...handlers}
      {...props}
    />
  )
  return handlers
}

describe('TurnComposer', () => {
  afterEach(cleanup)

  it('lists Player and the scene characters as actors', () => {
    renderComposer()

    const options = Array.from(screen.getByLabelText('Actor').querySelectorAll('option'))
    expect(options.map((o) => o.textContent)).toEqual(['Player', 'Harbor Guard'])
  })

  it('disables the character model and Send for a player with empty text', () => {
    renderComposer({ text: '   ' })

    expect(screen.getByLabelText('Character LLM')).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('enables Send for a player with text and submits', async () => {
    const { onSubmit } = renderComposer({ text: 'Look around' })

    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('allows Trigger with empty guidance and enables the character model', () => {
    renderComposer({ actor: 'guard' })

    expect(screen.getByRole('button', { name: 'Trigger' })).toBeEnabled()
    expect(screen.getByLabelText('Character LLM')).toBeEnabled()
    expect(screen.getByLabelText('Guidance')).toBeInTheDocument()
  })

  it('reports actor, text and model changes', async () => {
    const { onActorChange, onTextChange, onCharacterModelChange } = renderComposer({
      actor: 'guard',
    })

    await userEvent.selectOptions(screen.getByLabelText('Actor'), 'player')
    await userEvent.type(screen.getByLabelText('Guidance'), 'a')
    await userEvent.selectOptions(screen.getByLabelText('Character LLM'), 'model-b')

    expect(onActorChange).toHaveBeenCalledWith('player')
    expect(onTextChange).toHaveBeenCalledWith('a')
    expect(onCharacterModelChange).toHaveBeenCalledWith('model-b')
  })

  it('shows the narrator progress label for a player turn', () => {
    renderComposer({ text: 'Go', sending: true })

    expect(screen.getByText('Narrator is writing')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('shows the combined progress label for a character turn', () => {
    renderComposer({ actor: 'guard', sending: true })

    expect(screen.getByText('Character and narrator are working')).toBeInTheDocument()
  })

  it('shows retry controls and calls the cancel handler', async () => {
    const onCancelRetry = vi.fn()
    renderComposer({ retrying: true, onCancelRetry, text: 'Try again' })

    expect(screen.getByRole('status')).toHaveTextContent('Retrying last paragraph')
    await userEvent.click(screen.getByRole('button', { name: 'Cancel retry' }))

    expect(onCancelRetry).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('button', { name: 'Replace last paragraph' })).toBeEnabled()
  })

  it('uses the retry submit label for a character actor', () => {
    renderComposer({ actor: 'guard', retrying: true })

    expect(screen.getByRole('button', { name: 'Replace last paragraph' })).toBeEnabled()
    expect(screen.queryByRole('button', { name: 'Trigger' })).not.toBeInTheDocument()
  })
})
