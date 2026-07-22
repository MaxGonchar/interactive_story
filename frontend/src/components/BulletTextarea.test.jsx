import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BulletTextarea from './BulletTextarea'

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
})
