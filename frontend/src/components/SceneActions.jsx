function SceneActions({ finished, sceneSummary, onFinish }) {
  if (finished) {
    return (
      <div>
        <p>{sceneSummary ?? 'No summary available.'}</p>
      </div>
    )
  }

  return (
    <div>
      <button onClick={onFinish}>Finish Scene</button>
    </div>
  )
}

export default SceneActions
