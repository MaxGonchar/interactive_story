import { useState, useRef, useEffect } from 'react'
import { inlineEditTextarea } from '../styles'
import { EditIcon, StepBackIcon } from './icons'

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
      el.scrollIntoView?.({ block: 'nearest' })
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
    <div className="step-item">
      {editing ? (
        <>
          <textarea
            ref={textareaRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            style={inlineEditTextarea}
          />
          <div className="step-item__edit-actions">
            <button onClick={handleSave} disabled={saveDisabled}>Save</button>
            <button onClick={handleCancel}>Cancel</button>
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
              ><EditIcon style={{ width: '1rem', height: '1rem' }} /></button>
              <button
                className="msg-action-btn"
                onClick={() => onReturn(step.id)}
                aria-label="Return to this step"
                title="Return to this step"
              ><StepBackIcon style={{ width: '1rem', height: '1rem' }} /></button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default StepItem
