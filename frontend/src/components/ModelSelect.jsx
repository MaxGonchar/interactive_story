function ModelSelect({
  id,
  label,
  models,
  value,
  onChange,
  disabled = false,
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
        disabled={disabled}
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>{model.name}</option>
        ))}
      </select>
    </label>
  )
}

export default ModelSelect
