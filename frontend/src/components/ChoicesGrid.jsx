function ChoicesGrid({ choices, onSelect, onRegenerate, disabled = false }) {
  return (
    <div className="choices-grid-wrapper">
      <div className="choices-grid">
        {choices.map((choice, i) => (
          <button
            key={i}
            className="choice-button"
            onClick={() => onSelect(choice.action, choice.consequence)}
            disabled={disabled}
          >
            {choice.action}
          </button>
        ))}
      </div>
      <button
        className="choices-grid__regenerate"
        onClick={onRegenerate}
        disabled={disabled}
      >
        Regenerate
      </button>
    </div>
  )
}

export default ChoicesGrid
