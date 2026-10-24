import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { inlineEditTextarea } from '../styles'
import { DeleteIcon, EditIcon } from './icons'

function StoryItem({
  item,
  isOpening = false,
  isLast = false,
  onEdit,
  onDelete,
  disabled = false,
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(item.narration)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      await onEdit(item.id, draft)
      setEditing(false)
    } catch (err) {
      setError(err.message ?? 'Failed to save paragraph')
    } finally {
      setSaving(false)
    }
  }

  function handleCancel() {
    setDraft(item.narration)
    setError(null)
    setEditing(false)
  }

  const showDelete = isLast && !isOpening && Boolean(onDelete)
  const saveDisabled = saving || draft.trim() === '' || draft === item.narration

  return (
    <article className="story-item">
      {editing ? (
        <div className="story-item__edit">
          <textarea
            aria-label="Edit paragraph"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            maxLength={4000}
            disabled={saving}
            style={inlineEditTextarea}
          />
          <div className="story-item__edit-actions">
            <button onClick={handleSave} disabled={saveDisabled} type="button">
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button onClick={handleCancel} disabled={saving} type="button">
              Cancel
            </button>
          </div>
          {error && <p className="story-item__error" role="alert">{error}</p>}
        </div>
      ) : (
        <div className="story-item__content">
          <div className="message-md">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.narration}</ReactMarkdown>
          </div>
          {!disabled && (
            <div className="story-item__actions" role="group" aria-label="Paragraph actions">
              {onEdit && (
                <button
                  className="msg-action-btn"
                  onClick={() => {
                    setDraft(item.narration)
                    setError(null)
                    setEditing(true)
                  }}
                  aria-label="Edit paragraph"
                  title="Edit"
                  type="button"
                >
                  <EditIcon className="msg-action-icon" />
                </button>
              )}
              {showDelete && (
                <button
                  className="msg-action-btn"
                  onClick={() => onDelete(item.id)}
                  aria-label="Delete paragraph"
                  title="Delete"
                  type="button"
                >
                  <DeleteIcon className="msg-action-icon" />
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </article>
  )
}

export default StoryItem
