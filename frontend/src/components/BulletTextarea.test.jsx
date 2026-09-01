import React, { useState } from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BulletTextarea from './BulletTextarea'

// Wires value/onChange to real state, mirroring how NewScenePage uses BulletTextarea.
function StatefulBulletTextarea({ initialValue }) {
  const [value, setValue] = useState(initialValue)
  return <BulletTextarea value={value} onChange={setValue} />
}

describe('BulletTextarea', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders items as bullet lines', () => {
    render(<BulletTextarea value={['Alpha', 'Beta']} onChange={vi.fn()} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea.value).toBe('- Alpha\n- Beta')
  })

  it('renders an empty bullet "- " when value is an empty array', () => {
    render(<BulletTextarea value={[]} onChange={vi.fn()} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea.value).toBe('- ')
  })

  it('calls onChange with parsed array when user edits content', async () => {
    const onChange = vi.fn()
    render(<BulletTextarea value={[]} onChange={onChange} />)
    const textarea = screen.getByRole('textbox')
    await userEvent.clear(textarea)
    await userEvent.type(textarea, '- Hello')
    expect(onChange).toHaveBeenLastCalledWith(['Hello'])
  })

  it('respects the disabled prop', () => {
    render(<BulletTextarea value={['item']} onChange={vi.fn()} disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('keeps the caret at the edit point when fixing a typo mid-word with a real onChange round trip', async () => {
    render(<StatefulBulletTextarea initialValue={['Hello Wrold']} />)
    const textarea = screen.getByRole('textbox')

    // Place caret right after "Wr" (before "old") and delete one character to fix the typo.
    await userEvent.click(textarea)
    const caretIndex = textarea.value.indexOf('Wrold') + 2
    textarea.setSelectionRange(caretIndex, caretIndex)
    await userEvent.keyboard('{Backspace}')

    expect(textarea.value).toBe('- Hello Wold')
    expect(textarea.selectionStart).toBe(caretIndex - 1)
    expect(textarea.selectionEnd).toBe(caretIndex - 1)
  })
})
