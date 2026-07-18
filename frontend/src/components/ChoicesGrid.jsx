function ChoicesGrid({ choices, onSelect, onRegenerate, disabled = false }) {
  return (
    <div style={{ marginTop: 'var(--space-lg)' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 'var(--space-md)',
      }}>
        {choices.map((choice, i) => (
          <button
            key={i}
            onClick={() => onSelect(choice.action, choice.consequence)}
            disabled={disabled}
            style={{
              padding: 'var(--space-md)',
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
        style={{ marginTop: 'var(--space-md)' }}
      >
        Regenerate
      </button>
    </div>
  )
}

export default ChoicesGrid
