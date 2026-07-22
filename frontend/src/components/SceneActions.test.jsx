import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SceneActions from './SceneActions'

describe('SceneActions', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders the scene summary text when finished is true', () => {
    render(<SceneActions finished sceneSummary="Great scene summary" onFinish={vi.fn()} />)
    expect(screen.getByText('Great scene summary')).toBeInTheDocument()
  })

  it('renders "No summary available." when finished is true and sceneSummary is null', () => {
    render(<SceneActions finished sceneSummary={null} onFinish={vi.fn()} />)
    expect(screen.getByText('No summary available.')).toBeInTheDocument()
  })

  it('renders a textarea and Finish Scene button when finished is false', () => {
    render(<SceneActions finished={false} sceneSummary={null} onFinish={vi.fn()} />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Finish Scene' })).toBeInTheDocument()
  })

  it('Finish Scene button is disabled when textarea is empty', () => {
    render(<SceneActions finished={false} sceneSummary={null} onFinish={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Finish Scene' })).toBeDisabled()
  })

  it('clicking Finish Scene calls onFinish with trimmed summary text', async () => {
    const onFinish = vi.fn()
    render(<SceneActions finished={false} sceneSummary={null} onFinish={onFinish} />)
    await userEvent.type(screen.getByRole('textbox'), '  My summary  ')
    await userEvent.click(screen.getByRole('button', { name: 'Finish Scene' }))
    expect(onFinish).toHaveBeenCalledWith('My summary')
  })
})
