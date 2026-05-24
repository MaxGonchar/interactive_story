import MessageItem from './MessageItem'

function MessageList({ messages = [], onEdit, disabled }) {
  if (messages.length === 0) {
    return <p>No messages yet.</p>
  }

  return (
    <div>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} onEdit={onEdit} disabled={disabled} />
      ))}
    </div>
  )
}

export default MessageList
