import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import StoryList from './StoryList'
import { makeStory } from '../tests/factories'

describe('StoryList', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders a list item for each story', () => {
    const stories = [makeStory(), makeStory(), makeStory()]
    render(<StoryList stories={stories} onSelect={vi.fn()} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(stories.length)
  })

  it('each item shows the story title', () => {
    const stories = [makeStory({ title: 'Alpha' }), makeStory({ title: 'Beta' })]
    render(<StoryList stories={stories} onSelect={vi.fn()} />)
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.getByText('Beta')).toBeInTheDocument()
  })

  it('clicking a story item calls onSelect with the story object', async () => {
    const story = makeStory({ title: 'My Story' })
    const onSelect = vi.fn()
    render(<StoryList stories={[story]} onSelect={onSelect} />)
    await userEvent.click(screen.getByText('My Story'))
    expect(onSelect).toHaveBeenCalledWith(story)
  })

  it('renders "No stories available" when list is empty', () => {
    render(<StoryList stories={[]} onSelect={vi.fn()} />)
    expect(screen.getByText('No stories available')).toBeInTheDocument()
  })
})
