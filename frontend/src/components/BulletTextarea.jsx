import { useEffect, useRef, useState } from 'react'

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

function toText(value) {
  return value.length > 0 ? value.map((item) => BULLET + item).join('\n') : BULLET
}

function BulletTextarea({ value, onChange, ...rest }) {
  const [text, setText] = useState(() => toText(value))
  const prevValueRef = useRef(value)

  useEffect(() => {
    if (value !== prevValueRef.current) {
      prevValueRef.current = value
      setText(toText(value))
    }
  }, [value])

  function handleChange(e) {
    const newText = e.target.value
    setText(newText)
    onChange(parseItems(newText))
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      e.preventDefault()
      const { selectionStart, selectionEnd } = e.target
      const before = text.slice(0, selectionStart)
      const after = text.slice(selectionEnd)
      const newText = before + '\n' + BULLET + after
      setText(newText)
      onChange(parseItems(newText))
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
    const newText = before + normalised + after
    setText(newText)
    onChange(parseItems(newText))
  }

  return (
    <textarea
      value={text}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      onPaste={handlePaste}
      {...rest}
    />
  )
}

export default BulletTextarea
