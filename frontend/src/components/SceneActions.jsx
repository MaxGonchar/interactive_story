import { useState } from 'react'

function SceneActions({ finished, sceneSummary, onFinish }) {
  const [summaryText, setSummaryText] = useState('')

  if (finished) {
    return (
      <div>
        <p>{sceneSummary ?? 'No summary available.'}</p>
      </div>
    )
  }

  return (
    <div>
      <textarea
        value={summaryText}
        onChange={(e) => setSummaryText(e.target.value)}
        maxLength={2000}
        placeholder="Write a summary for this scene…"
        style={{
          width: '100%',
          boxSizing: 'border-box',
          font: 'inherit',
          border: '1px solid var(--border)',
          borderRadius: '4px',
          padding: '8px',
          resize: 'vertical',
          color: 'var(--text)',
          background: 'var(--bg)',
        }}
      />
      <button
        onClick={() => onFinish(summaryText.trim())}
        disabled={!summaryText.trim()}
      >
        Finish Scene
      </button>
    </div>
  )
}

export default SceneActions

