import { useEffect, useRef } from 'react'
import StoryItem from './StoryItem'

function StoryTimeline({ items }) {
  const endRef = useRef(null)
  const itemCount = items.length

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' })
  }, [itemCount])

  return (
    <div className="story-timeline">
      {items.map((item) => (
        <StoryItem key={item.id} item={item} />
      ))}
      <div ref={endRef} className="scene-message-list__end-anchor" />
    </div>
  )
}

export default StoryTimeline
