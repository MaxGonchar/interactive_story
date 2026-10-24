import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

  it('offers Edit on the opening paragraph and Delete only on the last paragraph', () => {
    const items = [
      makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' }),
      makeCharacterSceneItem({ id: 'last', narration: 'Last.' }),
    ]
    render(<StoryTimeline items={items} onEdit={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getAllByRole('button', { name: 'Edit paragraph' })).toHaveLength(2)
    expect(screen.getAllByRole('button', { name: 'Delete paragraph' })).toHaveLength(1)
  })

  it('forwards Delete for the last paragraph', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()
    const items = [
      makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' }),
      makeCharacterSceneItem({ id: 'last', narration: 'Last.' }),
    ]
    render(<StoryTimeline items={items} onEdit={vi.fn()} onDelete={onDelete} />)

    await user.click(screen.getByRole('button', { name: 'Delete paragraph' }))

    expect(onDelete).toHaveBeenCalledWith('last')
  })

  it('hides paragraph actions when disabled', () => {
    render(
      <StoryTimeline
        items={[makeCharacterSceneItem()]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        disabled
      />
    )

    expect(screen.queryByRole('button', { name: 'Edit paragraph' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()
  })
})
