import { useState, useRef, useEffect } from 'react'

function StepItem({ step, onEdit, onReturn, disabled = false }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(step.text)
  const [saving, setSaving] = useState(false)
  const textareaRef = useRef(null)

  useEffect(() => {
    if (editing && textareaRef.current) {
      const el = textareaRef.current
      el.style.height = 'auto'
      el.style.height = `${el.scrollHeight}px`
    }
  }, [editing, draft])

  const handleSave = async () => {
    setSaving(true)
    try {
      await onEdit(step.id, draft)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setDraft(step.text)
    setEditing(false)
  }

  const saveDisabled = saving || draft.trim() === '' || draft === step.text

  return (
    <div className="step-item" style={{ margin: '12px 0', padding: '12px', borderRadius: '8px', background: 'var(--code-bg)', border: '1px solid var(--border)' }}>
      {editing ? (
        <>
          <textarea
            ref={textareaRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              background: 'transparent',
              border: 'none',
              borderBottom: '1px solid var(--border)',
              outline: 'none',
              resize: 'none',
              overflow: 'hidden',
              font: 'inherit',
              color: 'inherit',
              padding: '0',
            }}
          />
          <div style={{ marginTop: '8px' }}>
            <button onClick={handleSave} disabled={saveDisabled}>Save</button>
            <button onClick={handleCancel} style={{ marginLeft: '8px' }}>Cancel</button>
          </div>
        </>
      ) : (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
          <p style={{ margin: 0, flex: 1 }}>{step.text}</p>
          {!disabled && (
            <div style={{ display: 'flex', gap: '4px', flexShrink: 0 }}>
              <button
                className="msg-action-btn"
                onClick={() => { setDraft(step.text); setEditing(true) }}
                aria-label="Edit step"
                title="Edit"
              >✏</button>
              <button
                className="msg-action-btn"
                onClick={() => onReturn(step.id)}
                aria-label="Return to this step"
                title="Return to this step"
              >↩</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default StepItem
