import MessageItem from './MessageItem'

function MessageList({ messages = [] }) {
  if (messages.length === 0) {
    return <p>No messages yet.</p>
  }

  return (
    <div>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  )
}

export default MessageList
