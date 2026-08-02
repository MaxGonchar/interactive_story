import { useState } from 'react'
import { inputBase } from '../styles'

function MessageComposer({ onSend, disabled = false, leadingAction = null }) {
  const [text, setText] = useState('')

  async function handleSend() {
    const trimmed = text.trim()
    if (!trimmed) return
    try {
      await onSend(trimmed)
      setText('')
    } catch {
      // leave text intact so user can retry
    }
  }

  return (
    <div className="message-composer" role="group" aria-label="Message composer">
      <textarea
        className="message-composer__textarea"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder={disabled ? 'Scene is finished' : 'Your message…'}
        style={inputBase}
      />
      <div className="message-composer__actions" role="group" aria-label="Message composer actions">
        {leadingAction}
        <button
          className="message-composer__send"
          onClick={handleSend}
          disabled={disabled || text.trim() === ''}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default MessageComposer
