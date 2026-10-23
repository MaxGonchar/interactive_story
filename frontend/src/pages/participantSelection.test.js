import { describe, it, expect } from 'vitest'
import { updateParticipantSelection } from './participantSelection'

describe('updateParticipantSelection', () => {
  it('removes a newly selected player from the NPC selection', () => {
    const result = updateParticipantSelection(
      { playerCharacterId: '', npcCharacterIds: ['hero', 'guard'] },
      { type: 'player', characterId: 'hero' }
    )

    expect(result).toEqual({
      playerCharacterId: 'hero',
      npcCharacterIds: ['guard'],
    })
  })

  it('clears the player when that character is toggled as an NPC', () => {
    const result = updateParticipantSelection(
      { playerCharacterId: 'hero', npcCharacterIds: [] },
      { type: 'npc', characterId: 'hero' }
    )

    expect(result).toEqual({
      playerCharacterId: '',
      npcCharacterIds: ['hero'],
    })
  })

  it('toggles an NPC without changing a different player', () => {
    const result = updateParticipantSelection(
      { playerCharacterId: 'hero', npcCharacterIds: ['guard'] },
      { type: 'npc', characterId: 'guard' }
    )

    expect(result).toEqual({
      playerCharacterId: 'hero',
      npcCharacterIds: [],
    })
  })
})
