import MessageItem from './MessageItem'

function MessageList({ messages = [], onEdit, onDelete, disabled }) {
  if (messages.length === 0) {
    return <p>No messages yet.</p>
  }

  const lastUserIdx = messages.map((m) => m.role).lastIndexOf('user')

  return (
    <div>
      {messages.map((message, index) => (
        <MessageItem
          key={message.id}
          message={message}
          onEdit={onEdit}
          disabled={disabled}
          onDelete={!disabled && index === lastUserIdx ? onDelete : undefined}
        />
      ))}
    </div>
  )
}

export default MessageList
