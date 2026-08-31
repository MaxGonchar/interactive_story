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

  it('renders both buttons and calls onSelect independently when choices have duplicate action and consequence', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    const duplicateChoices = [
      { action: 'Wait', consequence: 'Nothing happens' },
      { action: 'Wait', consequence: 'Nothing happens' },
    ]
    render(<ChoicesGrid choices={duplicateChoices} onSelect={onSelect} onRegenerate={vi.fn()} />)

    const buttons = screen.getAllByText('Wait')
    expect(buttons).toHaveLength(2)

    await user.click(buttons[1])

    expect(onSelect).toHaveBeenCalledWith('Wait', 'Nothing happens')
  })

  it('shows ProcessingLabel for the clicked choice when pendingAction matches choice key', () => {
    const onSelect = vi.fn()
    const pendingActionKey = 'Open the door::A gust of wind blows in'
    render(
      <ChoicesGrid
        choices={choices}
        onSelect={onSelect}
        onRegenerate={vi.fn()}
        pendingAction={pendingActionKey}
      />
    )

    expect(screen.getByText(/Continuing/)).toBeInTheDocument()
    expect(screen.queryByText('Open the door')).not.toBeInTheDocument()
  })

  it('disables all choice buttons when pendingAction is set', () => {
    const pendingActionKey = 'Open the door::A gust of wind blows in'
    render(
      <ChoicesGrid
        choices={choices}
        onSelect={vi.fn()}
        onRegenerate={vi.fn()}
        pendingAction={pendingActionKey}
      />
    )

    expect(screen.getByRole('button', { name: /Continuing/ })).toBeDisabled()
    expect(screen.getByText('Turn back')).toBeDisabled()
  })

  it('shows ProcessingLabel for regenerate button when pendingAction is "regenerate"', () => {
    render(
      <ChoicesGrid
        choices={choices}
        onSelect={vi.fn()}
        onRegenerate={vi.fn()}
        pendingAction="regenerate"
      />
    )

    expect(screen.getByRole('button', { name: /Regenerating/ })).toBeInTheDocument()
  })

  it('disables regenerate button and choice buttons when pendingAction is "regenerate"', () => {
    render(
      <ChoicesGrid
        choices={choices}
        onSelect={vi.fn()}
        onRegenerate={vi.fn()}
        pendingAction="regenerate"
      />
    )

    expect(screen.getByRole('button', { name: /Regenerating/ })).toBeDisabled()
    expect(screen.getByText('Open the door')).toBeDisabled()
  })

  it('shows normal choice text when pendingAction is null', () => {
    render(
      <ChoicesGrid
        choices={choices}
        onSelect={vi.fn()}
        onRegenerate={vi.fn()}
        pendingAction={null}
      />
    )

    expect(screen.getByText('Open the door')).toBeInTheDocument()
    expect(screen.getByText('Turn back')).toBeInTheDocument()
  })
})
