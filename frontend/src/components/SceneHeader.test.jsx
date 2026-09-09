import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import SceneHeader from './SceneHeader'
import { makeModel, makeScene } from '../tests/factories'

describe('SceneHeader', () => {
  it('renders the selected model and available model names', () => {
    const primaryModel = makeModel({ id: 'model-primary', name: 'Primary Model' })
    const alternateModel = makeModel({ id: 'model-alternate', name: 'Alternate Model' })

    render(
      <SceneHeader
        scene={makeScene()}
        models={[primaryModel, alternateModel]}
        selectedModelId={primaryModel.id}
        onModelChange={vi.fn()}
      />
    )

    expect(screen.getByRole('combobox', { name: 'Model' })).toHaveValue(primaryModel.id)
    expect(screen.getByRole('option', { name: 'Primary Model' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Alternate Model' })).toBeInTheDocument()
  })

  it('reports model changes and disables the selector when unavailable', async () => {
    const model = makeModel({ id: 'model-primary', name: 'Primary Model' })
    const alternateModel = makeModel({ id: 'model-alternate', name: 'Alternate Model' })
    const onModelChange = vi.fn()
    const user = userEvent.setup()

    const { rerender } = render(
      <SceneHeader
        scene={makeScene()}
        models={[model, alternateModel]}
        selectedModelId={model.id}
        onModelChange={onModelChange}
      />
    )

    await user.selectOptions(screen.getByRole('combobox', { name: 'Model' }), alternateModel.id)

    expect(onModelChange).toHaveBeenCalledWith(alternateModel.id)

    rerender(
      <SceneHeader
        scene={makeScene({ finished: true })}
        models={[model, alternateModel]}
        selectedModelId={model.id}
        onModelChange={onModelChange}
        disabled
      />
    )

    expect(screen.getByRole('combobox', { name: 'Model' })).toBeDisabled()
  })
})