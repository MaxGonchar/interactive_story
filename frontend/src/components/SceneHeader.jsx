function SceneHeader({ scene }) {
  return (
    <div>
      <h2>Scene {scene.id}</h2>
      <span>{scene.finished ? 'Finished' : 'Active'}</span>
    </div>
  )
}

export default SceneHeader
