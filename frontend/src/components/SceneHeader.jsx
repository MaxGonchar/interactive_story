function SceneHeader({ scene }) {
  return (
    <div className="scene-header">
      <h2>Scene {scene.id}</h2>
      <span>{scene.finished ? 'Finished' : 'Active'}</span>
    </div>
  )
}

export default SceneHeader
