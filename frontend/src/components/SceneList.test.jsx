import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SceneList from './SceneList'
import { makeScene } from '../tests/factories'

describe('SceneList', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders a list item for each scene', () => {
    const scenes = [makeScene(), makeScene(), makeScene()]
    render(<SceneList scenes={scenes} onSelect={vi.fn()} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(scenes.length)
  })

  it('each item shows the scene id', () => {
    const scene = makeScene({ id: 'scene-abc' })
    render(<SceneList scenes={[scene]} onSelect={vi.fn()} />)
    expect(screen.getByText(/scene-abc/i)).toBeInTheDocument()
  })

  it('clicking a scene item calls onSelect with the scene id', async () => {
    const scene = makeScene({ id: 'scene-xyz' })
    const onSelect = vi.fn()
    render(<SceneList scenes={[scene]} onSelect={onSelect} />)
    await userEvent.click(screen.getByText(/scene-xyz/i))
    expect(onSelect).toHaveBeenCalledWith('scene-xyz')
  })

  it('renders "No scenes available" when list is empty', () => {
    render(<SceneList scenes={[]} onSelect={vi.fn()} />)
    expect(screen.getByText('No scenes available')).toBeInTheDocument()
  })
})
