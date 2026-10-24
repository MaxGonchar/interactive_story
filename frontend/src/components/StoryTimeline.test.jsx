import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import StoryTimeline from './StoryTimeline'
import { makeCharacterSceneItem } from '../tests/factories'

describe('StoryTimeline', () => {
  const scrollIntoView = vi.fn()

  beforeEach(() => {
    scrollIntoView.mockReset()
    Element.prototype.scrollIntoView = scrollIntoView
  })

  afterEach(cleanup)

  it('renders items in order', () => {
    const items = [
      makeCharacterSceneItem({ narration: 'First.' }),
      makeCharacterSceneItem({ narration: 'Second.' }),
    ]

    render(<StoryTimeline items={items} />)

    expect(screen.getAllByRole('article').map((el) => el.textContent)).toEqual([
      'First.',
      'Second.',
    ])
  })

  it('scrolls to the end on load', () => {
    render(<StoryTimeline items={[makeCharacterSceneItem()]} />)

    expect(scrollIntoView).toHaveBeenCalledTimes(1)
  })

  it('scrolls again when the item count changes', () => {
    const first = makeCharacterSceneItem()
    const { rerender } = render(<StoryTimeline items={[first]} />)

    rerender(<StoryTimeline items={[first, makeCharacterSceneItem()]} />)

    expect(scrollIntoView).toHaveBeenCalledTimes(2)
  })

  it('does not scroll when an item is edited but the count is unchanged', () => {
    const first = makeCharacterSceneItem({ narration: 'Before.' })
    const { rerender } = render(<StoryTimeline items={[first]} />)

    rerender(<StoryTimeline items={[{ ...first, narration: 'After.' }]} />)

    expect(screen.getByText('After.')).toBeInTheDocument()
    expect(scrollIntoView).toHaveBeenCalledTimes(1)
  })
})
