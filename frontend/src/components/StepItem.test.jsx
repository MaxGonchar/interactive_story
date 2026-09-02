import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { makeMessage } from '../tests/factories'
import StepItem from './StepItem'

describe('StepItem', () => {
  it('renders edit and return action buttons', () => {
    const message = makeMessage({ content: 'Example step' })
    const step = { id: message.id, text: message.content }
    render(<StepItem step={step} onEdit={vi.fn()} onReturn={vi.fn()} />)

    expect(screen.getByLabelText('Edit step')).toBeInTheDocument()
    expect(screen.getByLabelText('Return to this step')).toBeInTheDocument()
  })

  it('enters edit mode and shows save and cancel controls', async () => {
    const user = userEvent.setup()
    const message = makeMessage({ content: 'Editable step' })
    const step = { id: message.id, text: message.content }

    render(<StepItem step={step} onEdit={vi.fn()} onReturn={vi.fn()} />)

    await user.click(screen.getByLabelText('Edit step'))

    expect(screen.getByRole('textbox')).toHaveValue('Editable step')
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
  })

  it('scrolls the whole edit block (including Save button) into view when entering edit mode', async () => {
    const scrollIntoView = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoView
    const user = userEvent.setup()
    const message = makeMessage({ content: 'Editable step' })
    const step = { id: message.id, text: message.content }

    render(<StepItem step={step} onEdit={vi.fn()} onReturn={vi.fn()} />)

    await user.click(screen.getByLabelText('Edit step'))

    expect(scrollIntoView).toHaveBeenCalledWith({ block: 'nearest' })
    const scrolledElement = scrollIntoView.mock.instances[0]
    expect(within(scrolledElement).getByRole('textbox')).toBeInTheDocument()
    expect(within(scrolledElement).getByRole('button', { name: 'Save' })).toBeInTheDocument()
  })
})
