import { useState } from 'react'

function MessageItem({ message, onEdit, disabled = false }) {
  const isUser = message.role === 'user'
  const label = isUser ? 'You' : 'Narrator'

  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(message.content)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!onEdit) return
    setSaving(true)
    try {
      await onEdit(message.id, draft)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setDraft(message.content)
    setEditing(false)
  }

  const saveDisabled = saving || draft.trim() === '' || draft === message.content

  const wrapperStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: isUser ? 'flex-end' : 'flex-start',
    margin: '8px 0',
  }

  const bubbleStyle = {
    maxWidth: '70%',
    padding: '8px 12px',
    borderRadius: '8px',
    background: isUser ? 'var(--accent-bg)' : 'var(--code-bg)',
    border: `1px solid ${isUser ? 'var(--accent-border)' : 'var(--border)'}`,
  }

  const labelStyle = {
    fontSize: '0.75em',
    color: 'var(--text)',
    marginBottom: '4px',
  }

  return (
    <div style={wrapperStyle}>
      <span style={labelStyle}>{label}</span>
      <div style={bubbleStyle}>
        {editing ? (
          <>
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              maxLength={4000}
              rows={4}
              style={{ width: '100%', boxSizing: 'border-box' }}
            />
            <div>
              <button onClick={handleSave} disabled={saveDisabled}>Save</button>
              <button onClick={handleCancel}>Cancel</button>
            </div>
          </>
        ) : (
          <>
            <p style={{ margin: 0 }}>{message.content}</p>
            {!disabled && onEdit && (
              <button
                className="message-edit-btn"
                onClick={() => setEditing(true)}
                aria-label="Edit message"
              >
                ✏️
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MessageItem
