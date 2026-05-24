function StoryList({ stories = [], onSelect }) {
  if (stories.length === 0) {
    return <p>No stories available</p>
  }

  return (
    <ul>
      {stories.map((story) => (
        <li key={story.id} className="clickable" onClick={() => onSelect(story.id)}>
          {story.title}
        </li>
      ))}
    </ul>
  )
}

export default StoryList
