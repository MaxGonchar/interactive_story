function SceneList({ scenes = [], activeSceneId, onSelect }) {
  if (scenes.length === 0) {
    return <p>No scenes available</p>
  }

  return (
    <ul>
      {scenes.map((scene) => (
        <li key={scene.id} className="clickable" onClick={() => onSelect(scene.id)}>
          Scene {scene.id}
          {scene.id === activeSceneId && ' (active)'}
          {scene.finished && ' (finished)'}
        </li>
      ))}
    </ul>
  )
}

export default SceneList
