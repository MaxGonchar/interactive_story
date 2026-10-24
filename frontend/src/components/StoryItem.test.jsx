import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
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

  it('enters edit mode and saves the edited narration', async () => {
    const user = userEvent.setup()
    const item = makeCharacterSceneItem({ id: 'item-1', narration: 'Original.' })
    const onEdit = vi.fn().mockResolvedValue()
    render(<StoryItem item={item} onEdit={onEdit} />)

    await user.click(screen.getByRole('button', { name: 'Edit paragraph' }))
    await user.clear(screen.getByRole('textbox', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Updated.')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(onEdit).toHaveBeenCalledWith('item-1', 'Updated.')
    expect(await screen.findByText('Original.')).toBeInTheDocument()
    expect(screen.queryByRole('textbox', { name: 'Edit paragraph' })).not.toBeInTheDocument()
  })

  it('cancels editing without saving the draft', async () => {
    const user = userEvent.setup()
    const onEdit = vi.fn()
    render(
      <StoryItem
        item={makeCharacterSceneItem({ narration: 'Original.' })}
        onEdit={onEdit}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Edit paragraph' }))
    await user.clear(screen.getByRole('textbox', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Draft.')
    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(screen.getByText('Original.')).toBeInTheDocument()
    expect(onEdit).not.toHaveBeenCalled()
  })

  it('keeps the draft open and shows an inline error when saving fails', async () => {
    const user = userEvent.setup()
    const onEdit = vi.fn().mockRejectedValue(new Error('Save failed'))
    render(
      <StoryItem
        item={makeCharacterSceneItem({ narration: 'Original.' })}
        onEdit={onEdit}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Edit paragraph' }))
    await user.clear(screen.getByRole('textbox', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Draft.')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Save failed')
    expect(screen.getByRole('textbox', { name: 'Edit paragraph' })).toHaveValue('Draft.')
  })

  it('shows a saving state while the save request is pending', async () => {
    const user = userEvent.setup()
    let finishSave
    const onEdit = vi.fn(() => new Promise((resolve) => { finishSave = resolve }))
    render(
      <StoryItem
        item={makeCharacterSceneItem({ narration: 'Original.' })}
        onEdit={onEdit}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Edit paragraph' }))
    await user.type(screen.getByRole('textbox', { name: 'Edit paragraph' }), 'Updated.')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(screen.getByRole('button', { name: 'Saving...' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled()
    finishSave()
    await waitFor(() => expect(screen.queryByRole('textbox')).not.toBeInTheDocument())
  })

  it('only shows Delete for a last paragraph that is not the opening item', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()
    const openingItem = makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' })
    const lastItem = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    const onEdit = vi.fn()

    const { rerender } = render(
      <StoryItem
        item={openingItem}
        isOpening
        isLast
        onEdit={onEdit}
        onDelete={onDelete}
      />
    )

    expect(screen.getByRole('button', { name: 'Edit paragraph' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Delete paragraph' })).not.toBeInTheDocument()

    rerender(
      <StoryItem item={lastItem} isLast onEdit={onEdit} onDelete={onDelete} />
    )
    await user.click(screen.getByRole('button', { name: 'Delete paragraph' }))

    expect(onDelete).toHaveBeenCalledWith('last')
  })

  it('only shows Retry for a last paragraph that is not the opening item', async () => {
    const user = userEvent.setup()
    const onRetry = vi.fn()
    const openingItem = makeCharacterSceneItem({ id: 'opening', narration: 'Opening.' })
    const lastItem = makeCharacterSceneItem({ id: 'last', narration: 'Last.' })
    const { rerender } = render(
      <StoryItem item={openingItem} isOpening isLast onRetry={onRetry} />
    )

    expect(screen.queryByRole('button', { name: 'Retry paragraph' })).not.toBeInTheDocument()

    rerender(<StoryItem item={lastItem} isLast onRetry={onRetry} />)
    await user.click(screen.getByRole('button', { name: 'Retry paragraph' }))

    expect(onRetry).toHaveBeenCalledWith(lastItem)
  })

  it('disables paragraph actions when retry mode is active', () => {
    render(
      <StoryItem
        item={makeCharacterSceneItem()}
        isLast
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRetry={vi.fn()}
        actionsDisabled
      />
    )

    expect(screen.getByRole('button', { name: 'Edit paragraph' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Delete paragraph' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Retry paragraph' })).toBeDisabled()
  })
})
