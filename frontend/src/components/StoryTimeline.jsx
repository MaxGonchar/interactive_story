import { useEffect, useRef } from 'react'
import StoryItem from './StoryItem'

function StoryTimeline({ items, onEdit, onDelete, disabled = false }) {
  const endRef = useRef(null)
  const itemCount = items.length

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' })
  }, [itemCount])

  return (
    <div className="story-timeline">
      {items.map((item, index) => (
        <StoryItem
          key={item.id}
          item={item}
          isOpening={index === 0}
          isLast={index === itemCount - 1}
          onEdit={onEdit}
          onDelete={onDelete}
          disabled={disabled}
        />
      ))}
      <div ref={endRef} className="scene-message-list__end-anchor" />
    </div>
  )
}

export default StoryTimeline
