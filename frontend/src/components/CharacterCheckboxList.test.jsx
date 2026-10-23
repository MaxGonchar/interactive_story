import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import CharacterCheckboxList from './CharacterCheckboxList'
import { makeCharacter } from '../tests/factories'

describe('CharacterCheckboxList', () => {
  it('renders the selected characters and disables the player character', () => {
    render(
      <CharacterCheckboxList
        label="Characters"
        characters={[
          makeCharacter({ id: 'hero', name: 'Hero' }),
          makeCharacter({ id: 'guard', name: 'Guard' }),
        ]}
        selectedIds={['guard']}
        onToggle={vi.fn()}
        disabledCharacterId="hero"
      />
    )

    expect(screen.getByRole('group', { name: 'Characters' })).toBeInTheDocument()
    expect(screen.getByRole('checkbox', { name: 'Hero' })).toBeDisabled()
    expect(screen.getByRole('checkbox', { name: 'Guard' })).toBeChecked()
  })

  it('reports a character toggle', async () => {
    const onToggle = vi.fn()
    const user = userEvent.setup()

    render(
      <CharacterCheckboxList
        label="Characters"
        characters={[makeCharacter({ id: 'guard', name: 'Guard' })]}
        selectedIds={[]}
        onToggle={onToggle}
      />
    )

    await user.click(screen.getByRole('checkbox', { name: 'Guard' }))

    expect(onToggle).toHaveBeenCalledWith('guard')
  })
})
