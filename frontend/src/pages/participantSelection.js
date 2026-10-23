export function updateParticipantSelection(
  selection,
  { type, characterId }
) {
  if (type === 'player') {
    return {
      playerCharacterId: characterId,
      npcCharacterIds: selection.npcCharacterIds.filter((id) => id !== characterId),
    }
  }

  const npcCharacterIds = selection.npcCharacterIds.includes(characterId)
    ? selection.npcCharacterIds.filter((id) => id !== characterId)
    : [...selection.npcCharacterIds, characterId]

  return {
    playerCharacterId:
      selection.playerCharacterId === characterId ? '' : selection.playerCharacterId,
    npcCharacterIds,
  }
}
