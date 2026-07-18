function StoryList({ stories = [], onSelect }) {
  if (stories.length === 0) {
    return <p>No stories available</p>
  }

  return (
    <ul className="story-list">
      {stories.map((story) => (
        <li key={story.id} className="clickable" onClick={() => onSelect(story)}>
          {story.title}
          {story.type && (
            <span className="story-type-badge">
              {story.type === 'choice_driven' ? 'Choice' : 'Scene'}
            </span>
          )}
        </li>
      ))}
    </ul>
  )
}

export default StoryList
