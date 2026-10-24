import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import StoryItem from './StoryItem'
import { makeCharacterSceneItem } from '../tests/factories'

afterEach(cleanup)

describe('StoryItem', () => {
  it('renders the narration as markdown', () => {
    render(<StoryItem item={makeCharacterSceneItem({ narration: 'A **bold** move.' })} />)

    expect(screen.getByText('bold').tagName).toBe('STRONG')
  })

  it('does not render player input or character action', () => {
    render(
      <StoryItem
        item={makeCharacterSceneItem({
          narration: 'Narration.',
          input: { action: 'Secret input' },
          character_action: 'Secret action',
        })}
      />
    )

    expect(screen.getByText('Narration.')).toBeInTheDocument()
    expect(screen.queryByText('Secret input')).not.toBeInTheDocument()
    expect(screen.queryByText('Secret action')).not.toBeInTheDocument()
  })
})
