import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import CharacterSelect from './CharacterSelect'
import { makeCharacter } from '../tests/factories'

describe('CharacterSelect', () => {
  it('renders a placeholder, optional Narrator option, and characters', () => {
    render(
      <CharacterSelect
        id="player"
        label="Player"
        characters={[makeCharacter({ id: 'hero', name: 'Hero' })]}
        value=""
        onChange={vi.fn()}
        includeNarrator
      />
    )

    expect(screen.getByRole('option', { name: '— select —' })).toHaveValue('')
    expect(screen.getByRole('option', { name: 'Narrator' })).toHaveValue('__narrator__')
    expect(screen.getByRole('option', { name: 'Hero' })).toHaveValue('hero')
  })

  it('reports a selected character and omits Narrator by default', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()

    render(
      <CharacterSelect
        id="player"
        label="Player"
        characters={[makeCharacter({ id: 'hero', name: 'Hero' })]}
        value=""
        onChange={onChange}
      />
    )

    await user.selectOptions(screen.getByRole('combobox', { name: 'Player' }), 'hero')

    expect(onChange).toHaveBeenCalledWith('hero')
    expect(screen.queryByRole('option', { name: 'Narrator' })).not.toBeInTheDocument()
  })
})
