import { useState } from 'react'
import { generateSceneSummary } from '../api/scenes'
import BulletTextarea from './BulletTextarea'
import { inputBase } from '../styles'
import ProcessingLabel from './ProcessingLabel'

function FinishModal({ onSubmit, onCancel, storyId, sceneId }) {
  const [items, setItems] = useState([])
  const [validationError, setValidationError] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState(null)

  async function handleGenerate() {
    setIsGenerating(true)
    setGenerateError(null)
    try {
      const data = await generateSceneSummary(storyId, sceneId)
      setItems(data.data.summary)
    } catch (err) {
      setGenerateError(err.message ?? 'Failed to generate summary.')
    } finally {
      setIsGenerating(false)
    }
  }

  function handleSubmit() {
    if (items.length === 0) {
      setValidationError('Please add at least 1 summary item.')
      return
    }
    if (items.length > 100) {
      setValidationError('Summary cannot exceed 100 items.')
      return
    }
    setValidationError(null)
    onSubmit(items)
  }

  return (
    <div className="modal-overlay">
      <div className="modal-panel">
        <h3 style={{ margin: 0, color: 'var(--text-h)' }}>Finish Scene</h3>
        <BulletTextarea
          value={items}
          onChange={setItems}
          disabled={isGenerating}
          rows={14}
          style={{ ...inputBase, resize: 'vertical' }}
        />
        {validationError && (
          <p style={{ margin: 0, color: 'var(--error)', fontSize: '14px' }}>
            {validationError}
          </p>
        )}
        {generateError && (
          <p style={{ margin: 0, color: 'var(--error)', fontSize: '14px' }}>
            {generateError}
          </p>
        )}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button onClick={handleGenerate} disabled={isGenerating} style={{ minWidth: '150px' }}>
            {isGenerating ? <ProcessingLabel verb="Generating" /> : 'Generate Summary'}
          </button>
          <button onClick={onCancel} disabled={isGenerating}>Cancel</button>
          <button onClick={handleSubmit} disabled={isGenerating}>Submit</button>
        </div>
      </div>
    </div>
  )
}

export default FinishModal
