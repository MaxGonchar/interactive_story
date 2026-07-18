import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { inlineEditTextarea } from '../styles'

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

  return (
    <div className="message-wrapper" style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}>
      <span className="message-label">{label}</span>
      <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--narrator'}`} style={{ width: editing ? '70%' : undefined }}>
        {editing ? (
          <>
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              maxLength={4000}
              style={inlineEditTextarea}
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
