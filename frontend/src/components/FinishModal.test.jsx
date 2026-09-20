import { render, screen, act, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import FinishModal from './FinishModal'
import { generateSceneSummary } from '../api/scenes'

vi.mock('../api/scenes')

describe('FinishModal', () => {
  const defaultProps = {
    onSubmit: vi.fn(),
    onCancel: vi.fn(),
    storyId: 'story-1',
    sceneId: 'scene-1',
  }

  beforeEach(() => {
    vi.resetAllMocks()
    defaultProps.onSubmit = vi.fn()
    defaultProps.onCancel = vi.fn()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders modal overlay with "Finish Scene" heading', () => {
    render(<FinishModal {...defaultProps} />)
    expect(screen.getByText('Finish Scene')).toBeInTheDocument()
  })

  it('Submit button is present', () => {
    render(<FinishModal {...defaultProps} />)
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument()
  })

  it('clicking Submit with empty items shows validation error', async () => {
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(screen.getByText('Please add at least 1 summary item.')).toBeInTheDocument()
    expect(defaultProps.onSubmit).not.toHaveBeenCalled()
  })

  it('clicking Submit with valid items calls onSubmit with the items', async () => {
    generateSceneSummary.mockResolvedValue({
      data: { summary: ['Item one', 'Item two'] },
    })
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))
    await screen.findByDisplayValue(/Item one/)
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(defaultProps.onSubmit).toHaveBeenCalledWith(['Item one', 'Item two'])
  })

  it('clicking Cancel calls onCancel', async () => {
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(defaultProps.onCancel).toHaveBeenCalled()
  })

  it('clicking "Generate" calls generateSceneSummary and populates items on success', async () => {
    generateSceneSummary.mockResolvedValue({
      data: { summary: ['A thing happened', 'Another thing'] },
    })
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))
    expect(generateSceneSummary).toHaveBeenCalledWith('story-1', 'scene-1')
    await screen.findByDisplayValue(/A thing happened/)
  })

  it('Generate button is disabled while generation is in-flight', async () => {
    let resolveGenerate
    generateSceneSummary.mockImplementation(
      () => new Promise((resolve) => { resolveGenerate = resolve })
    )
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))
    expect(screen.getByText(/Generating/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Generating/ })).toBeDisabled()
    await act(async () => { resolveGenerate({ data: { summary: [] } }) })
  })

  it('shows error message when generateSceneSummary throws', async () => {
    generateSceneSummary.mockRejectedValue(new Error('Server error'))
    render(<FinishModal {...defaultProps} />)
    await userEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))
    await screen.findByText('Server error')
  })

  it('updates the generation timer while pending and hides it after success', async () => {
    let resolveGenerate
    generateSceneSummary.mockImplementation(
      () => new Promise((resolve) => { resolveGenerate = resolve })
    )
    vi.useFakeTimers()
    render(<FinishModal {...defaultProps} />)
    fireEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))

    expect(screen.getByLabelText('Generating elapsed time')).toBeInTheDocument()
    act(() => {
      vi.advanceTimersByTime(23450)
    })
    expect(screen.getByText('00:23:450')).toBeInTheDocument()

    await act(async () => {
      resolveGenerate({ data: { summary: ['A completed item'] } })
    })

    expect(screen.queryByLabelText('Generating elapsed time')).not.toBeInTheDocument()
  })

  it('hides the generation timer and preserves the error on failure', async () => {
    generateSceneSummary.mockRejectedValue(new Error('Generation failed'))
    vi.useFakeTimers()
    render(<FinishModal {...defaultProps} />)
    fireEvent.click(screen.getByRole('button', { name: 'Generate Summary' }))

    expect(screen.getByLabelText('Generating elapsed time')).toBeInTheDocument()
    await act(async () => {
      await Promise.resolve()
    })

    expect(screen.getByText('Generation failed')).toBeInTheDocument()
    expect(screen.queryByLabelText('Generating elapsed time')).not.toBeInTheDocument()
  })
})
