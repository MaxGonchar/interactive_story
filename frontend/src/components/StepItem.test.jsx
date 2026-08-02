import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import StepItem from './StepItem'

describe('StepItem', () => {
  it('renders edit and return action buttons', () => {
    const step = { id: '1', text: 'Example step' }
    render(<StepItem step={step} onEdit={vi.fn()} onReturn={vi.fn()} />)

    expect(screen.getByLabelText('Edit step')).toBeInTheDocument()
    expect(screen.getByLabelText('Return to this step')).toBeInTheDocument()
  })
})
