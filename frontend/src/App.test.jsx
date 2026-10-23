import React from 'react'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, it, expect } from 'vitest'
import App from './App'

afterEach(() => {
  cleanup()
  window.history.replaceState({}, '', '/')
})

describe('App character-scene routes', () => {
  it('renders the character-scene creation placeholder', () => {
    window.history.replaceState({}, '', '/stories/story-1/character-scenes/new')
    render(<App />)

    expect(screen.getByText('Character scene creation page is not available yet.')).toBeInTheDocument()
  })

  it('renders the character-scene placeholder', () => {
    window.history.replaceState({}, '', '/stories/story-1/character-scenes/scene-1')
    render(<App />)

    expect(screen.getByText('Character scene page is not available yet.')).toBeInTheDocument()
  })
})
