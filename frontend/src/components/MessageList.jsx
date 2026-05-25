import MessageItem from './MessageItem'

function MessageList({ messages = [], onEdit, onDelete, onRegenerate, disabled }) {
  if (messages.length === 0) {
    return <p>No messages yet.</p>
  }

  const lastUserIdx = messages.map((m) => m.role).lastIndexOf('user')
  const lastAssistantIdx = messages.map((m) => m.role).lastIndexOf('assistant')

  // Only pass onRegenerate if lastAssistantIdx > 0 and not disabled
  const shouldShowRegenerate =
    typeof onRegenerate === 'function' &&
    !disabled &&
    lastAssistantIdx > 0

  return (
    <div>
      {messages.map((message, index) => (
        <MessageItem
          key={message.id}
          message={message}
          onEdit={onEdit}
          disabled={disabled}
          onDelete={!disabled && index === lastUserIdx ? onDelete : undefined}
          onRegenerate={shouldShowRegenerate && index === lastAssistantIdx ? onRegenerate : undefined}
        />
      ))}
    </div>
  )
}

export default MessageList
