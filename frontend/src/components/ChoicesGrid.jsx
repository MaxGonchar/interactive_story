function ChoicesGrid({ choices, onSelect, onRegenerate, disabled = false }) {
  return (
    <div style={{ marginTop: '16px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
      }}>
        {choices.map((choice, i) => (
          <button
            key={i}
            onClick={() => onSelect(choice.action, choice.consequence)}
            disabled={disabled}
            style={{
              padding: '12px',
              borderRadius: '8px',
              background: 'var(--accent-bg)',
              border: '1px solid var(--accent-border)',
              cursor: disabled ? 'not-allowed' : 'pointer',
              textAlign: 'left',
              font: 'inherit',
              color: 'inherit',
            }}
          >
            {choice.action}
          </button>
        ))}
      </div>
      <button
        onClick={onRegenerate}
        disabled={disabled}
        style={{ marginTop: '12px' }}
      >
        Regenerate
      </button>
    </div>
  )
}

export default ChoicesGrid
