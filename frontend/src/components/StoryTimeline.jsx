import { useEffect, useRef } from 'react'
import StoryItem from './StoryItem'

function StoryTimeline({
  items,
  onEdit,
  onDelete,
  onRetry,
  disabled = false,
  actionsDisabled = false,
}) {
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
          onRetry={onRetry}
          disabled={disabled}
          actionsDisabled={actionsDisabled}
        />
      ))}
      <div ref={endRef} className="scene-message-list__end-anchor" />
    </div>
  )
}

export default StoryTimeline
