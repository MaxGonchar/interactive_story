function CharacterSelect({
  id,
  label,
  characters,
  value,
  onChange,
  includeNarrator = false,
  narratorValue = '__narrator__',
  placeholder = '— select —',
  className = '',
}) {
  return (
    <label htmlFor={id} className="new-scene-page__field">
      <span className="new-scene-page__label">{label}</span>
      <select
        id={id}
        className={`form-control__select ${className}`.trim()}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {placeholder !== null && <option value="">{placeholder}</option>}
        {includeNarrator && <option value={narratorValue}>Narrator</option>}
        {characters.map((character) => (
          <option key={character.id} value={character.id}>
            {character.name}
          </option>
        ))}
      </select>
    </label>
  )
}

export default CharacterSelect
