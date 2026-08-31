import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ProcessingLabel from './ProcessingLabel'

describe('ProcessingLabel', () => {
  it('renders verb text and processing dots', () => {
    render(<ProcessingLabel verb="Sending" />)
    const label = screen.getByText(/Sending/)
    expect(label).toBeInTheDocument()
    expect(label.querySelector('.processing-dots')).toBeInTheDocument()
  })

  it('applies processing-dots class to the dots span', () => {
    render(<ProcessingLabel verb="Generating" />)
    const dots = screen.getByText(/Generating/).querySelector('.processing-dots')
    expect(dots).toHaveClass('processing-dots')
  })

  it('uses default verb when not provided', () => {
    render(<ProcessingLabel />)
    expect(screen.getByText(/Processing/)).toBeInTheDocument()
  })
})
