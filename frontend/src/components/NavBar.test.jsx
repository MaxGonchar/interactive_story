import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import NavBar from './NavBar'

function renderNavBar() {
  return render(
    <MemoryRouter initialEntries={['/somewhere']}>
      <Routes>
        <Route path="/somewhere" element={<NavBar />} />
        <Route path="/stories" element={<><NavBar /><p>Stories Page</p></>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('NavBar', () => {
  it('renders a link with the "Stories" tooltip', () => {
    renderNavBar()
    expect(screen.getByTitle('Stories')).toBeInTheDocument()
  })

  it('links to /stories', () => {
    renderNavBar()
    expect(screen.getByTitle('Stories')).toHaveAttribute('href', '/stories')
  })

  it('renders the stories SVG icon inside the link', () => {
    renderNavBar()
    const link = screen.getByTitle('Stories')
    expect(link.querySelector('svg')).toBeInTheDocument()
  })

  it('navigates to the stories page when clicked', async () => {
    renderNavBar()
    await userEvent.click(screen.getByTitle('Stories'))
    expect(screen.getByText('Stories Page')).toBeInTheDocument()
  })
})
