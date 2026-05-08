import { useState } from 'react'

function MessageComposer({ onSend, disabled = false }) {
  const [text, setText] = useState('')

  function handleSend() {
    const trimmed = text.trim()
    if (!trimmed) return
    onSend(trimmed)
    setText('')
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
