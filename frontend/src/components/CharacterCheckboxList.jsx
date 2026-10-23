function CharacterCheckboxList({
  label,
  characters,
  selectedIds,
  onToggle,
  disabledCharacterId = null,
}) {
  return (
    <fieldset className="new-scene-page__fieldset">
      <legend className="new-scene-page__legend">{label}</legend>
      <div className="new-scene-page__checkbox-list">
        {characters.map((character) => (
          <label key={character.id} className="new-scene-page__checkbox-row">
            <input
              type="checkbox"
              checked={selectedIds.includes(character.id)}
              disabled={character.id === disabledCharacterId}
              onChange={() => onToggle(character.id)}
            />
            {character.name}
          </label>
        ))}
      </div>
    </fieldset>
  )
}

export default CharacterCheckboxList
