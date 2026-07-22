import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MessageComposer from './MessageComposer'

describe('MessageComposer', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders a textarea and a Send button', () => {
    render(<MessageComposer onSend={vi.fn()} />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument()
  })

  it('Send button is disabled when textarea is empty', () => {
    render(<MessageComposer onSend={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('Send button is disabled when disabled prop is true', async () => {
    render(<MessageComposer onSend={vi.fn()} disabled={true} />)
    await userEvent.type(screen.getByRole('textbox'), 'hello')
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('Send button is enabled when textarea has non-whitespace content', async () => {
    render(<MessageComposer onSend={vi.fn()} />)
    await userEvent.type(screen.getByRole('textbox'), 'hello')
    expect(screen.getByRole('button', { name: 'Send' })).toBeEnabled()
  })

  it('clicking Send calls onSend with trimmed text', async () => {
    const onSend = vi.fn().mockResolvedValue(undefined)
    render(<MessageComposer onSend={onSend} />)
    await userEvent.type(screen.getByRole('textbox'), '  hello  ')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))
    expect(onSend).toHaveBeenCalledWith('hello')
  })

  it('textarea is cleared after successful send', async () => {
    const onSend = vi.fn().mockResolvedValue(undefined)
    render(<MessageComposer onSend={onSend} />)
    await userEvent.type(screen.getByRole('textbox'), 'hello')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))
    expect(screen.getByRole('textbox')).toHaveValue('')
  })

  it('textarea retains content when onSend throws (retry scenario)', async () => {
    const onSend = vi.fn().mockRejectedValue(new Error('Network error'))
    render(<MessageComposer onSend={onSend} />)
    await userEvent.type(screen.getByRole('textbox'), 'hello')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))
    expect(screen.getByRole('textbox')).toHaveValue('hello')
  })

  it('placeholder text changes based on disabled prop', () => {
    const { rerender } = render(<MessageComposer onSend={vi.fn()} disabled={false} />)
    expect(screen.getByRole('textbox')).toHaveAttribute('placeholder', 'Your message…')

    rerender(<MessageComposer onSend={vi.fn()} disabled={true} />)
    expect(screen.getByRole('textbox')).toHaveAttribute('placeholder', 'Scene is finished')
  })
})
