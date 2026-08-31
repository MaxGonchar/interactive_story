import ProcessingLabel from './ProcessingLabel'

function ChoicesGrid({ choices, onSelect, onRegenerate, disabled = false, pendingAction = null }) {
  // API returns no id, so derive a stable key from content and disambiguate duplicates
  const seen = new Map()
  const keyedChoices = choices.map((choice) => {
    const base = `${choice.action}::${choice.consequence}`
    const count = seen.get(base) ?? 0
    seen.set(base, count + 1)
    return { choice, key: count === 0 ? base : `${base}::${count}` }
  })

  return (
    <div className="choices-grid-wrapper">
      <div className="choices-grid">
        {keyedChoices.map(({ choice, key }) => {
          const isClickedChoice = pendingAction === key
          return (
            <button
              key={key}
              className="choice-button"
              onClick={() => onSelect(choice.action, choice.consequence)}
              disabled={disabled || pendingAction !== null}
              style={{ minWidth: '100px' }}
            >
              {isClickedChoice ? <ProcessingLabel verb="Continuing" /> : choice.action}
            </button>
          )
        })}
      </div>
      <button
        className="choices-grid__regenerate"
        onClick={onRegenerate}
        disabled={disabled || pendingAction !== null}
        style={{ minWidth: '120px' }}
      >
        {pendingAction === 'regenerate' ? <ProcessingLabel verb="Regenerating" /> : 'Regenerate'}
      </button>
    </div>
  )
}

export default ChoicesGrid
