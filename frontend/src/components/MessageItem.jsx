function MessageItem({ message }) {
  const isUser = message.role === 'user'
  const label = isUser ? 'You' : 'Narrator'

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
        <p style={{ margin: 0 }}>{message.content}</p>
      </div>
    </div>
  )
}

export default MessageItem
