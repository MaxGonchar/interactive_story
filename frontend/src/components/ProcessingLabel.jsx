/**
 * ProcessingLabel
 *
 * Renders "{verb}…" with an animated pulsing dots indicator.
 * Used consistently across all LLM-call operations.
 */
function ProcessingLabel({ verb = 'Processing' }) {
  return (
    <span className="processing-label">
      {verb}
      <span className="processing-dots" />
    </span>
  )
}

export default ProcessingLabel
