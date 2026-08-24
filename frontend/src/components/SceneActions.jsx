import { useState } from 'react'
import { inputBase } from '../styles'

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
        style={{ ...inputBase, width: '100%', boxSizing: 'border-box', resize: 'vertical' }}
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

