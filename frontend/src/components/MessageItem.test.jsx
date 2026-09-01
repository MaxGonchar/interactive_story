import React from 'react'
import { render, screen, act, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MessageItem from './MessageItem'
import { makeMessage } from '../tests/factories'

describe('MessageItem', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders "You" label for user messages', () => {
    const msg = makeMessage({ role: 'user' })
    render(<MessageItem message={msg} />)
    expect(screen.getByText('You')).toBeInTheDocument()
  })

  it('renders "Narrator" label for assistant messages', () => {
    const msg = makeMessage({ role: 'assistant' })
    render(<MessageItem message={msg} />)
    expect(screen.getByText('Narrator')).toBeInTheDocument()
  })

  it('shows edit button when onEdit is provided and disabled is false', () => {
    const msg = makeMessage()
    render(<MessageItem message={msg} onEdit={vi.fn()} disabled={false} />)
    expect(screen.getByLabelText('Edit message')).toBeInTheDocument()
  })

  it('does not show edit button when disabled is true', () => {
    const msg = makeMessage()
    render(<MessageItem message={msg} onEdit={vi.fn()} disabled={true} />)
    expect(screen.queryByLabelText('Edit message')).not.toBeInTheDocument()
  })

  it('clicking edit button switches to edit mode (textarea appears)', async () => {
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('scrolls the textarea into view when entering edit mode', async () => {
    const scrollIntoView = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoView
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    expect(scrollIntoView).toHaveBeenCalledWith({ block: 'nearest' })
  })

  it('Save button is disabled when draft equals original content', async () => {
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
  })

  it('Save button is disabled when draft is empty', async () => {
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    await userEvent.clear(screen.getByRole('textbox'))
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
  })

  it('Save button is enabled when draft differs from original', async () => {
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    await userEvent.type(screen.getByRole('textbox'), ' updated')
    expect(screen.getByRole('button', { name: 'Save' })).toBeEnabled()
  })

  it('clicking Save calls onEdit with correct message id and new content', async () => {
    const onEdit = vi.fn().mockResolvedValue(undefined)
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={onEdit} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    await userEvent.type(screen.getByRole('textbox'), ' updated')
    await userEvent.click(screen.getByRole('button', { name: 'Save' }))
    expect(onEdit).toHaveBeenCalledWith(msg.id, 'Hello world updated')
  })

  it('clicking Cancel restores original content and exits edit mode', async () => {
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    await userEvent.type(screen.getByRole('textbox'), ' updated')
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(screen.getByText('Hello world', { exact: false })).toBeInTheDocument()
  })

  it('shows Regenerate button for assistant messages when onRegenerate is provided', () => {
    const msg = makeMessage({ role: 'assistant' })
    render(<MessageItem message={msg} onRegenerate={vi.fn()} />)
    expect(screen.getByLabelText('Regenerate message')).toBeInTheDocument()
  })

  it('does not show Regenerate button for user messages', () => {
    const msg = makeMessage({ role: 'user' })
    render(<MessageItem message={msg} onRegenerate={vi.fn()} />)
    expect(screen.queryByLabelText('Regenerate message')).not.toBeInTheDocument()
  })

  it('Save button shows disabled state while save is in-flight', async () => {
    let resolveSave
    const onEdit = vi.fn().mockImplementation(
      () => new Promise((resolve) => { resolveSave = resolve })
    )
    const msg = makeMessage({ content: 'Hello world' })
    render(<MessageItem message={msg} onEdit={onEdit} />)
    await userEvent.click(screen.getByLabelText('Edit message'))
    await userEvent.type(screen.getByRole('textbox'), ' updated')
    await userEvent.click(screen.getByRole('button', { name: 'Save' }))
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
    await act(async () => { resolveSave() })
  })

  it('renders assistant actions inside one shared action container', () => {
    const msg = makeMessage({ role: 'assistant' })
    render(
      <MessageItem
        message={msg}
        onRegenerate={vi.fn()}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />
    )

    const actions = screen.getByRole('group', { name: 'Message actions' })
    expect(within(actions).getByLabelText('Regenerate message')).toBeInTheDocument()
    expect(within(actions).getByLabelText('Edit message')).toBeInTheDocument()
    expect(within(actions).getByLabelText('Delete message')).toBeInTheDocument()
  })

  it('renders user actions inside one shared action container', () => {
    const msg = makeMessage({ role: 'user' })
    render(
      <MessageItem
        message={msg}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />
    )

    const actions = screen.getByRole('group', { name: 'Message actions' })
    expect(within(actions).getByLabelText('Edit message')).toBeInTheDocument()
    expect(within(actions).getByLabelText('Delete message')).toBeInTheDocument()
    expect(within(actions).queryByLabelText('Regenerate message')).not.toBeInTheDocument()
  })

  it('opens edit mode with regenerated content when rerendered with same id and new content', async () => {
    const msg = makeMessage({ id: 'm1', content: 'Original content' })
    const { rerender } = render(<MessageItem message={msg} onEdit={vi.fn()} />)

    rerender(<MessageItem message={{ ...msg, content: 'Regenerated content' }} onEdit={vi.fn()} />)
    await userEvent.click(screen.getByLabelText('Edit message'))

    expect(screen.getByRole('textbox')).toHaveValue('Regenerated content')
  })

  it('closes edit mode when content changes while editing', async () => {
    const msg = makeMessage({ id: 'm1', content: 'Original content' })
    const { rerender } = render(<MessageItem message={msg} onEdit={vi.fn()} />)

    await userEvent.click(screen.getByLabelText('Edit message'))
    expect(screen.getByRole('textbox')).toBeInTheDocument()

    rerender(<MessageItem message={{ ...msg, content: 'Regenerated content' }} onEdit={vi.fn()} />)

    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
  })

  it('shows ProcessingLabel when regeneratingMessageId matches message id', () => {
    const msg = makeMessage({ id: 'm1', role: 'assistant', content: 'Original content' })
    render(<MessageItem message={msg} regeneratingMessageId="m1" />)
    expect(screen.getByText(/Regenerating/)).toBeInTheDocument()
    expect(screen.queryByText('Original content')).not.toBeInTheDocument()
  })

  it('does not show ProcessingLabel when regeneratingMessageId does not match message id', () => {
    const msg = makeMessage({ id: 'm1', role: 'assistant', content: 'Original content' })
    render(<MessageItem message={msg} regeneratingMessageId="m2" />)
    expect(screen.queryByText(/Regenerating/)).not.toBeInTheDocument()
    expect(screen.getByText('Original content', { exact: false })).toBeInTheDocument()
  })

  it('does not show ProcessingLabel when regeneratingMessageId is null', () => {
    const msg = makeMessage({ id: 'm1', role: 'assistant', content: 'Original content' })
    render(<MessageItem message={msg} regeneratingMessageId={null} />)
    expect(screen.queryByText(/Regenerating/)).not.toBeInTheDocument()
    expect(screen.getByText('Original content', { exact: false })).toBeInTheDocument()
  })

  it('hides message actions while regenerating', () => {
    const msg = makeMessage({ id: 'm1', role: 'assistant', content: 'Original content' })
    render(
      <MessageItem
        message={msg}
        onRegenerate={vi.fn()}
        regeneratingMessageId="m1"
      />
    )
    expect(screen.queryByLabelText('Regenerate message')).not.toBeInTheDocument()
  })
})
