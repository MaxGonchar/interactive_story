import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MessageList from './MessageList'
import { makeMessage } from '../tests/factories'

vi.mock('./MessageItem', () => ({
  default: ({ message, onEdit, onDelete, onRegenerate }) => (
    <div data-testid={`message-item-${message.id}`}>
      <span data-testid="role">{message.role}</span>
      {onEdit && <button data-testid="has-edit">edit</button>}
      {onDelete && <button data-testid="has-delete">delete</button>}
      {onRegenerate && <button data-testid="has-regenerate">regenerate</button>}
    </div>
  ),
}))

describe('MessageList', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders a MessageItem for each message in the list', () => {
    const messages = [makeMessage(), makeMessage(), makeMessage()]
    render(<MessageList messages={messages} />)
    messages.forEach((m) => {
      expect(screen.getByTestId(`message-item-${m.id}`)).toBeInTheDocument()
    })
  })

  it('passes onEdit to each MessageItem', () => {
    const onEdit = vi.fn()
    const messages = [makeMessage(), makeMessage()]
    render(<MessageList messages={messages} onEdit={onEdit} />)
    expect(screen.getAllByTestId('has-edit')).toHaveLength(2)
  })

  it('passes onDelete only to the last user message when not disabled', () => {
    const onDelete = vi.fn()
    const messages = [
      makeMessage({ role: 'user' }),
      makeMessage({ role: 'user' }),
    ]
    render(<MessageList messages={messages} onDelete={onDelete} />)
    // Only the last user message should have onDelete
    expect(screen.getAllByTestId('has-delete')).toHaveLength(1)
  })

  it('passes onRegenerate only to the last assistant message when lastAssistantIdx > 0 and not disabled', () => {
    const onRegenerate = vi.fn()
    const messages = [
      makeMessage({ role: 'user' }),
      makeMessage({ role: 'assistant' }),
      makeMessage({ role: 'assistant' }),
    ]
    render(<MessageList messages={messages} onRegenerate={onRegenerate} />)
    expect(screen.getAllByTestId('has-regenerate')).toHaveLength(1)
  })

  it('does not pass onRegenerate when lastAssistantIdx is 0', () => {
    const onRegenerate = vi.fn()
    // First and only message is assistant — lastAssistantIdx === 0
    const messages = [makeMessage({ role: 'assistant' })]
    render(<MessageList messages={messages} onRegenerate={onRegenerate} />)
    expect(screen.queryByTestId('has-regenerate')).not.toBeInTheDocument()
  })

  it('renders empty state without crashing when list is empty', () => {
    render(<MessageList messages={[]} />)
    expect(screen.getByText('No messages yet.')).toBeInTheDocument()
  })
})
