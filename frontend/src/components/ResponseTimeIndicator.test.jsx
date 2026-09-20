import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ResponseTimeIndicator from './ResponseTimeIndicator'

describe('ResponseTimeIndicator', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders the verb and zero-padded initial elapsed time', () => {
    render(<ResponseTimeIndicator verb="Generating" />)

    expect(screen.getByText('Generating')).toBeInTheDocument()
    expect(screen.getByText('00:00:000')).toBeInTheDocument()
  })

  it('formats minutes, seconds, and milliseconds with zero padding', () => {
    render(<ResponseTimeIndicator verb="Generating" />)

    act(() => {
      vi.advanceTimersByTime(125678)
    })

    expect(screen.getByText('02:05:670')).toBeInTheDocument()
  })

  it('updates the elapsed time every 10 milliseconds while active', () => {
    render(<ResponseTimeIndicator verb="Sending" />)

    act(() => {
      vi.advanceTimersByTime(12340)
    })

    expect(screen.getByText('00:12:340')).toBeInTheDocument()
  })

  it('cleans up the timer when it becomes inactive', () => {
    const { rerender } = render(<ResponseTimeIndicator verb="Sending" />)

    act(() => {
      vi.advanceTimersByTime(100)
    })
    rerender(<ResponseTimeIndicator verb="Sending" active={false} />)

    act(() => {
      vi.advanceTimersByTime(100)
    })

    expect(screen.getByText('00:00:100')).toBeInTheDocument()
  })

  it('announces completion and failure without announcing timer ticks', () => {
    const { rerender } = render(<ResponseTimeIndicator verb="Generating" />)
    const announcement = screen.getByRole('status')

    expect(announcement).toHaveTextContent('')

    act(() => {
      vi.advanceTimersByTime(100)
    })
    expect(announcement).toHaveTextContent('')

    rerender(<ResponseTimeIndicator verb="Generating" active={false} status="complete" />)
    expect(announcement).toHaveTextContent('Generating completed')

    rerender(<ResponseTimeIndicator verb="Generating" active={false} status="error" />)
    expect(announcement).toHaveTextContent('Generating failed')
  })
})