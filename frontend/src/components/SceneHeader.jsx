function SceneHeader({ scene }) {
  return (
    <div>
      <h2>Scene {scene.id}</h2>
      <span>{scene.finished ? 'Finished' : 'Active'}</span>
      <p>{scene.scene_description.entry_point}</p>
    </div>
  )
}

export default SceneHeader
