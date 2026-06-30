import { useState } from 'react'

function MessageComposer({ onSend, disabled = false }) {
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder={disabled ? 'Scene is finished' : 'Your message…'}
        style={{ resize: 'vertical', minHeight: '80px', padding: '8px' }}
      />
      <button
        onClick={handleSend}
        disabled={disabled || text.trim() === ''}
      >
        Send
      </button>
    </div>
  )
}

export default MessageComposer
