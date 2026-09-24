import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import SceneHeader from './SceneHeader'
import { makeModel, makeScene, makeStory } from '../tests/factories'

describe('SceneHeader', () => {
  it('renders the selected model and available model names', () => {
    const primaryModel = makeModel({ id: 'model-primary', name: 'Primary Model' })
    const alternateModel = makeModel({ id: 'model-alternate', name: 'Alternate Model' })

    render(<MemoryRouter><SceneHeader
      scene={makeScene()}
      storyId="story-1"
      storyTitle="Test Story"
      models={[primaryModel, alternateModel]}
      selectedModelId={primaryModel.id}
      onModelChange={vi.fn()}
    /></MemoryRouter>)

    expect(screen.getByRole('combobox', { name: 'Model' })).toHaveValue(primaryModel.id)
    expect(screen.getByRole('option', { name: 'Primary Model' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Alternate Model' })).toBeInTheDocument()
  })

  it('renders the parent story link before the scene title', () => {
    const story = makeStory({ title: 'A Story, With Punctuation!' })

    render(<MemoryRouter><SceneHeader
      scene={makeScene({ id: 'scene-7' })}
      storyId={story.id}
      storyTitle={story.title}
      models={[]}
      selectedModelId=""
      onModelChange={vi.fn()}
    /></MemoryRouter>)

    const header = screen.getByRole('heading', { name: 'Scene scene-7' }).parentElement
    expect(header.firstChild).toHaveTextContent(story.title)
    expect(screen.getByRole('link', { name: story.title })).toHaveAttribute('href', `/stories/${story.id}`)
  })

  it('reports model changes and disables the selector when unavailable', async () => {
    const model = makeModel({ id: 'model-primary', name: 'Primary Model' })
    const alternateModel = makeModel({ id: 'model-alternate', name: 'Alternate Model' })
    const onModelChange = vi.fn()
    const user = userEvent.setup()

    const { rerender } = render(<MemoryRouter><SceneHeader
      scene={makeScene()}
      storyId="story-1"
      storyTitle="Test Story"
      models={[model, alternateModel]}
      selectedModelId={model.id}
      onModelChange={onModelChange}
    /></MemoryRouter>)

    await user.selectOptions(screen.getByRole('combobox', { name: 'Model' }), alternateModel.id)

    expect(onModelChange).toHaveBeenCalledWith(alternateModel.id)

    rerender(<MemoryRouter><SceneHeader
      scene={makeScene({ finished: true })}
      storyId="story-1"
      storyTitle="Test Story"
      models={[model, alternateModel]}
      selectedModelId={model.id}
      onModelChange={onModelChange}
      disabled
    /></MemoryRouter>)

    expect(screen.getByRole('combobox', { name: 'Model' })).toBeDisabled()
    expect(screen.getByRole('link', { name: 'Test Story' })).toBeInTheDocument()
  })
})