import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { inlineEditTextarea } from '../styles'
import { DeleteIcon, EditIcon, RefreshIcon } from './icons'
import ProcessingLabel from './ProcessingLabel'

function MessageItem({ message, onEdit, onDelete, onRegenerate, disabled = false, regeneratingMessageId = null }) {
  const isUser = message.role === 'user'
  const label = isUser ? 'You' : 'Narrator'

  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(message.content)
  const [saving, setSaving] = useState(false)
  const textareaRef = useRef(null)
  const editBlockRef = useRef(null)

  useEffect(() => {
    if (editing && textareaRef.current) {
      const el = textareaRef.current
      el.style.height = 'auto'
      el.style.height = `${el.scrollHeight}px`
      // Scroll the whole edit block (textarea + Save/Cancel) into view, not just the textarea.
      editBlockRef.current?.scrollIntoView?.({ block: 'nearest' })
    }
  }, [editing, draft])

  // Regeneration reuses the same message id, so sync draft/edit state to new content.
  useEffect(() => {
    setDraft(message.content)
    setEditing(false)
  }, [message.id, message.content])

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
  const showRegenerate = message.role === 'assistant' && Boolean(onRegenerate)
  const showEdit = !disabled && Boolean(onEdit)
  const showDelete = Boolean(onDelete)
  const hasActions = showRegenerate || showEdit || showDelete
  const isRegenerating = regeneratingMessageId === message.id

  return (
    <div className="message-wrapper" style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}>
      <span className="message-label">{label}</span>
      <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--narrator'}`} style={{ width: editing ? '70%' : undefined }}>
        {editing ? (
          <div ref={editBlockRef}>
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
          </div>
        ) : isRegenerating ? (
          <ProcessingLabel verb="Regenerating" />
        ) : (
          <>
            <div className="message-md"><ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown></div>
            {hasActions && (
              <div className="message-actions" role="group" aria-label="Message actions">
                {showRegenerate && (
                  <button
                    className="msg-action-btn"
                    onClick={onRegenerate}
                    aria-label="Regenerate message"
                    type="button"
                  >
                       <RefreshIcon className="msg-action-icon" />
                  </button>
                )}
                {showEdit && (
                  <button
                    className="msg-action-btn"
                    onClick={() => setEditing(true)}
                    aria-label="Edit message"
                  >
                       <EditIcon className="msg-action-icon" />
                  </button>
                )}
                {showDelete && (
                  <button
                    className="msg-action-btn"
                    onClick={() => onDelete(message.id)}
                    aria-label="Delete message"
                  >
                       <DeleteIcon className="msg-action-icon" />
                  </button>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MessageItem
