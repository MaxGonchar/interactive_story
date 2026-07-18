import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function MessageItem({ message, onEdit, onDelete, onRegenerate, disabled = false }) {
  const isUser = message.role === 'user'
  const label = isUser ? 'You' : 'Narrator'

  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(message.content)
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
    width: editing ? '70%' : undefined,
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
      <div className="message-bubble" style={bubbleStyle}>
        {editing ? (
          <>
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              maxLength={4000}
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
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <button onClick={handleSave} disabled={saveDisabled}>Save</button>
              <button onClick={handleCancel}>Cancel</button>
            </div>
          </>
        ) : (
          <>
            <div className="message-md"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown></div>
            {/* Regenerate button: only for assistant messages, only if onRegenerate is provided */}
            {message.role === 'assistant' && onRegenerate && (
              <button
                className="msg-action-btn"
                onClick={onRegenerate}
                aria-label="Regenerate message"
                type="button"
              >
                ↺
              </button>
            )}
            {/* Existing edit/delete buttons */}
            {!disabled && onEdit && (
              <button
                className="edit-btn"
                onClick={() => setEditing(true)}
                aria-label="Edit message"
              >
                ✏️
              </button>
            )}
            {onDelete && (
              <button
                className="delete-btn"
                onClick={() => onDelete(message.id)}
                aria-label="Delete message"
              >
                ✕
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MessageItem
