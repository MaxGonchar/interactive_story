import { useState } from 'react'
import { generateSceneSummary } from '../api/scenes'
import BulletTextarea from './BulletTextarea'

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
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: 'var(--bg)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '24px',
          width: '576px',
          maxWidth: '90vw',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <h3 style={{ margin: 0, color: 'var(--text-h)' }}>Finish Scene</h3>
        <BulletTextarea
          value={items}
          onChange={setItems}
          disabled={isGenerating}
          rows={14}
          style={{
            resize: 'vertical',
            padding: '8px',
            fontFamily: 'var(--sans)',
            fontSize: '16px',
            border: '1px solid var(--border)',
            borderRadius: '4px',
          }}
        />
        {validationError && (
          <p style={{ margin: 0, color: 'red', fontSize: '14px' }}>
            {validationError}
          </p>
        )}
        {generateError && (
          <p style={{ margin: 0, color: 'red', fontSize: '14px' }}>
            {generateError}
          </p>
        )}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? 'Generating…' : 'Generate Summary'}
          </button>
          <button onClick={onCancel} disabled={isGenerating}>Cancel</button>
          <button onClick={handleSubmit} disabled={isGenerating}>Submit</button>
        </div>
      </div>
    </div>
  )
}

export default FinishModal
