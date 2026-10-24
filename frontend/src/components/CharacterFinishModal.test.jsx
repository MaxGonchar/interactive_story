import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import CharacterFinishModal from './CharacterFinishModal'
import {
  getCharacterMemoryDraft,
  getCharacterSceneSummaryDraft,
} from '../api/character_play'

vi.mock('../api/character_play')

const PARTICIPANTS = [
  { id: 'mora', name: 'Captain Mora' },
  { id: 'guard', name: 'Harbor Guard' },
]

function setup(props = {}) {
  const onSubmit = vi.fn().mockResolvedValue(undefined)
  const onCancel = vi.fn()
  render(
    <CharacterFinishModal
      storyId="s1"
      sceneId={1}
      participants={PARTICIPANTS}
      onSubmit={onSubmit}
      onCancel={onCancel}
      {...props}
    />
  )
  return { onSubmit, onCancel, user: userEvent.setup() }
}

function mockDrafts() {
  getCharacterSceneSummaryDraft.mockResolvedValue({ data: { summary: ['Sum'] } })
  getCharacterMemoryDraft.mockImplementation(async (_s, _sc, id) => ({
    data: { character_id: id, memory_updates: [`mem ${id}`] },
  }))
}

const tab = (name) => screen.getByRole('tab', { name: new RegExp(name) })

describe('CharacterFinishModal', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders tabs in order with badges and selects Summary', () => {
    setup()

    const tabs = screen.getAllByRole('tab')

    expect(tabs.map((t) => t.textContent)).toEqual([
      'SummaryEmpty',
      'Captain MoraEmpty',
      'Harbor GuardEmpty',
    ])
    expect(tabs[0]).toHaveAttribute('aria-selected', 'true')
    expect(tabs[1]).toHaveAttribute('aria-selected', 'false')
  })

  it('shows a single editor and keeps text across tab switches', async () => {
    const { user } = setup()

    await user.type(screen.getByRole('textbox'), 'hello')
    await user.click(tab('Captain Mora'))
    expect(screen.getAllByRole('textbox')).toHaveLength(1)
    await user.click(tab('Summary'))

    expect(screen.getByRole('textbox')).toHaveValue('- hello')
    expect(tab('Summary')).toHaveTextContent('Edited')
  })

  it('Generate all fills every tab', async () => {
    mockDrafts()
    const { user } = setup()

    await user.click(screen.getByRole('button', { name: 'Generate all' }))

    await waitFor(() => expect(tab('Harbor Guard')).toHaveTextContent('Generated'))
    expect(screen.getByRole('textbox')).toHaveValue('- Sum')
    expect(getCharacterMemoryDraft).toHaveBeenCalledTimes(2)
  })

  it('disables Finish while generating but keeps Cancel enabled', async () => {
    getCharacterSceneSummaryDraft.mockReturnValue(new Promise(() => {}))
    const { user } = setup()

    await user.click(screen.getByRole('button', { name: 'Regenerate this' }))

    expect(screen.getByRole('button', { name: 'Finish scene' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeEnabled()
    expect(screen.getByRole('status')).toHaveTextContent('Generating Summary')
  })

  it('shows per-tab error when generation fails', async () => {
    getCharacterSceneSummaryDraft.mockRejectedValue(new Error('boom'))
    const { user } = setup()

    await user.click(screen.getByRole('button', { name: 'Regenerate this' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('boom')
    expect(tab('Summary')).toHaveTextContent('Error')
  })

  it('Regenerate this only regenerates the active tab', async () => {
    mockDrafts()
    const { user } = setup()

    await user.click(tab('Captain Mora'))
    await user.click(screen.getByRole('button', { name: 'Regenerate this' }))

    await waitFor(() => expect(screen.getByRole('textbox')).toHaveValue('- mem mora'))
    expect(getCharacterMemoryDraft).toHaveBeenCalledTimes(1)
    expect(getCharacterSceneSummaryDraft).not.toHaveBeenCalled()
  })

  it('blocks submit with an invalid summary', async () => {
    const { user, onSubmit } = setup()

    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Please add at least 1 summary item.')
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('blocks submit with more than 100 summary items', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue({
      data: { summary: Array.from({ length: 101 }, (_, i) => `i${i}`) },
    })
    const { user, onSubmit } = setup()
    await user.click(screen.getByRole('button', { name: 'Regenerate this' }))
    await waitFor(() => expect(tab('Summary')).toHaveTextContent('Generated'))

    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Summary cannot exceed 100 items.')
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('asks for confirmation once for unresolved memory tabs, then submits', async () => {
    const { user, onSubmit } = setup()
    await user.type(screen.getByRole('textbox'), 'sum')

    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(screen.getByRole('alert')).toHaveTextContent(
      'No memory update was generated or entered for: Captain Mora, Harbor Guard. Select Finish scene again to confirm.'
    )
    expect(onSubmit).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(onSubmit).toHaveBeenCalledWith({
      sceneSummary: ['sum'],
      characterMemoryUpdates: { mora: [], guard: [] },
    })
  })

  it('resets the confirmation after an edit', async () => {
    const { user, onSubmit } = setup()
    await user.type(screen.getByRole('textbox'), 'sum')
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    await user.type(screen.getByRole('textbox'), 'x')

    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('resets the confirmation when generating', async () => {
    mockDrafts()
    const { user } = setup()
    await user.type(screen.getByRole('textbox'), 'sum')
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    await user.click(screen.getByRole('button', { name: 'Regenerate this' }))

    expect(screen.queryByText(/No memory update was generated/)).not.toBeInTheDocument()
  })

  it('submits directly when all memory tabs are generated', async () => {
    mockDrafts()
    const { user, onSubmit } = setup()
    await user.click(screen.getByRole('button', { name: 'Generate all' }))
    await waitFor(() => expect(tab('Harbor Guard')).toHaveTextContent('Generated'))

    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(onSubmit).toHaveBeenCalledWith({
      sceneSummary: ['Sum'],
      characterMemoryUpdates: { mora: ['mem mora'], guard: ['mem guard'] },
    })
  })

  it('shows an inline error and keeps edits when submit fails', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('save failed'))
    const { user } = setup({ onSubmit })
    await user.type(screen.getByRole('textbox'), 'sum')
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))
    await user.click(screen.getByRole('button', { name: 'Finish scene' }))

    expect(await screen.findByText('save failed')).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('- sum')
    expect(screen.getByRole('button', { name: 'Finish scene' })).toBeEnabled()
  })

  it('calls onCancel', async () => {
    const { user, onCancel } = setup()

    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(onCancel).toHaveBeenCalled()
  })
})
