import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ModelSelect from './ModelSelect'
import { makeModel } from '../tests/factories'

describe('ModelSelect', () => {
  it('renders available models and the selected value', () => {
    const models = [
      makeModel({ id: 'model-a', name: 'Model A' }),
      makeModel({ id: 'model-b', name: 'Model B' }),
    ]

    render(
      <ModelSelect
        id="model"
        label="Model"
        models={models}
        value="model-a"
        onChange={vi.fn()}
      />
    )

    expect(screen.getByRole('combobox', { name: 'Model' })).toHaveValue('model-a')
    expect(screen.getByRole('option', { name: 'Model B' })).toBeInTheDocument()
  })

  it('reports a model selection and respects disabled', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const models = [
      makeModel({ id: 'model-a', name: 'Model A' }),
      makeModel({ id: 'model-b', name: 'Model B' }),
    ]

    render(
      <ModelSelect
        id="model"
        label="Model"
        models={models}
        value="model-a"
        onChange={onChange}
      />
    )

    await user.selectOptions(screen.getByRole('combobox', { name: 'Model' }), 'model-b')

    expect(onChange).toHaveBeenCalledWith('model-b')
  })

  it('disables the selector when requested', () => {
    render(
      <ModelSelect
        id="model"
        label="Model"
        models={[makeModel({ id: 'model-a', name: 'Model A' })]}
        value="model-a"
        onChange={vi.fn()}
        disabled
      />
    )

    expect(screen.getByRole('combobox', { name: 'Model' })).toBeDisabled()
  })
})
