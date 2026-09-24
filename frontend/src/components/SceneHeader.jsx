import { Link } from 'react-router-dom'

function SceneHeader({ scene, storyId, storyTitle, models, selectedModelId, onModelChange, disabled = false }) {
  return (
    <div className="scene-header">
      <Link className="scene-header__story-link" to={`/stories/${storyId}`}>{storyTitle}</Link>
      <h2>Scene {scene.id}</h2>
      <span>{scene.finished ? 'Finished' : 'Active'}</span>
      <label className="scene-header__model-control">
        <span className="scene-header__model-label">Model</span>
        <select
          className="scene-header__model-select"
          value={selectedModelId}
          onChange={(event) => onModelChange(event.target.value)}
          disabled={disabled}
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>{model.name}</option>
          ))}
        </select>
      </label>
    </div>
  )
}

export default SceneHeader
