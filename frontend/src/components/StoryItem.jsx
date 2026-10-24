import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function StoryItem({ item }) {
  return (
    <article className="story-item">
      <div className="message-md">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.narration}</ReactMarkdown>
      </div>
    </article>
  )
}

export default StoryItem
