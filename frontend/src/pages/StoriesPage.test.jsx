import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import StoriesPage from './StoriesPage'
import { getStories } from '../api/stories'
import { makeStory } from '../tests/factories'

vi.mock('../api/stories')

function renderPage() {
  return render(
    <MemoryRouter>
      <StoriesPage />
    </MemoryRouter>
  )
}

describe('StoriesPage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading state', () => {
    getStories.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders stories list on success', async () => {
    const story = makeStory({ title: 'The Lost Kingdom' })
    getStories.mockResolvedValue({ data: [story] })
    renderPage()
    expect(await screen.findByText('The Lost Kingdom')).toBeInTheDocument()
  })

  it('renders error message on API failure', async () => {
    getStories.mockRejectedValue(new Error('Failed to fetch stories'))
    renderPage()
    expect(await screen.findByText('Failed to fetch stories')).toBeInTheDocument()
  })
})
