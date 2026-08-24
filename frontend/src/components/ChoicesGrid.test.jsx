import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ChoicesGrid from './ChoicesGrid'

const choices = [
  { action: 'Open the door', consequence: 'A gust of wind blows in' },
  { action: 'Turn back', consequence: 'You retreat to safety' },
]

describe('ChoicesGrid', () => {
  it('renders each choice action text', () => {
    render(<ChoicesGrid choices={choices} onSelect={vi.fn()} onRegenerate={vi.fn()} />)

    expect(screen.getByText('Open the door')).toBeInTheDocument()
    expect(screen.getByText('Turn back')).toBeInTheDocument()
  })

  it('calls onSelect with action and consequence when a choice is clicked', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(<ChoicesGrid choices={choices} onSelect={onSelect} onRegenerate={vi.fn()} />)

    await user.click(screen.getByText('Open the door'))

    expect(onSelect).toHaveBeenCalledWith('Open the door', 'A gust of wind blows in')
  })

  it('calls onRegenerate when the regenerate button is clicked', async () => {
    const user = userEvent.setup()
    const onRegenerate = vi.fn()
    render(<ChoicesGrid choices={choices} onSelect={vi.fn()} onRegenerate={onRegenerate} />)

    await user.click(screen.getByText('Regenerate'))

    expect(onRegenerate).toHaveBeenCalled()
  })

  it('disables all buttons when disabled prop is true', () => {
    render(<ChoicesGrid choices={choices} onSelect={vi.fn()} onRegenerate={vi.fn()} disabled />)

    expect(screen.getByText('Open the door')).toBeDisabled()
    expect(screen.getByText('Turn back')).toBeDisabled()
    expect(screen.getByText('Regenerate')).toBeDisabled()
  })
})
