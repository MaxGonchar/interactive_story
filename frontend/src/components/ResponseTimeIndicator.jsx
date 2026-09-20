import { useEffect, useRef, useState } from 'react'

function formatElapsedTime(elapsedMs) {
  const totalSeconds = Math.floor(elapsedMs / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  const milliseconds = elapsedMs % 1000

  return [minutes, seconds, milliseconds]
    .map((value, index) => String(value).padStart(index === 2 ? 3 : 2, '0'))
    .join(':')
}

function ResponseTimeIndicator({ verb = 'Processing', active = true, status = 'active' }) {
  const [elapsedMs, setElapsedMs] = useState(0)
  const startedAtRef = useRef(null)

  useEffect(() => {
    if (!active) {
      return undefined
    }

    startedAtRef.current = Date.now()
    const intervalId = window.setInterval(() => {
      setElapsedMs(Date.now() - startedAtRef.current)
    }, 10)

    return () => window.clearInterval(intervalId)
  }, [active])

  const announcement = status === 'complete'
    ? `${verb} completed`
    : status === 'error'
      ? `${verb} failed`
      : ''

  return (
    <span className="response-time-indicator">
      <span>{verb}</span>
      <span className="response-time-value" aria-label={`${verb} elapsed time`}>
        {formatElapsedTime(elapsedMs)}
      </span>
      <span className="response-time-announcement" role="status" aria-live="polite">
        {announcement}
      </span>
    </span>
  )
}

export default ResponseTimeIndicator