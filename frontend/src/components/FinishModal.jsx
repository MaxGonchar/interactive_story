import { useState } from 'react'
import { generateSceneSummary } from '../api/scenes'

const BULLET = '- '

function parseItems(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith(BULLET))
    .map((line) => line.slice(BULLET.length).trim())
    .filter((item) => item.length > 0)
}

function normalisePaste(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => (line.startsWith(BULLET) ? line : BULLET + line))
    .join('\n')
}

function FinishModal({ onSubmit, onCancel, storyId, sceneId }) {
  const [text, setText] = useState(BULLET)
  const [validationError, setValidationError] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState(null)

  async function handleGenerate() {
    setIsGenerating(true)
    setGenerateError(null)
    try {
      const data = await generateSceneSummary(storyId, sceneId)
      const bulletText = data.data.summary.map((item) => BULLET + item).join('\n')
      setText(bulletText)
    } catch (err) {
      setGenerateError(err.message ?? 'Failed to generate summary.')
    } finally {
      setIsGenerating(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      e.preventDefault()
      const { selectionStart, selectionEnd } = e.target
      const before = text.slice(0, selectionStart)
      const after = text.slice(selectionEnd)
      const newText = before + '\n' + BULLET + after
      setText(newText)
      // place cursor after the inserted bullet
      requestAnimationFrame(() => {
        e.target.selectionStart = selectionStart + 1 + BULLET.length
        e.target.selectionEnd = selectionStart + 1 + BULLET.length
      })
    }
  }

  function handlePaste(e) {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text')
    const { selectionStart, selectionEnd } = e.target
    const before = text.slice(0, selectionStart)
    const after = text.slice(selectionEnd)
    const normalised = normalisePaste(pasted)
    setText(before + normalised + after)
  }

  function handleSubmit() {
    const items = parseItems(text)
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
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
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
