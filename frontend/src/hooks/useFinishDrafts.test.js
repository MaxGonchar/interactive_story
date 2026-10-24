import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { SUMMARY_TAB, useFinishDrafts } from './useFinishDrafts'
import {
  getCharacterMemoryDraft,
  getCharacterSceneSummaryDraft,
} from '../api/character_play'

vi.mock('../api/character_play')

const IDS = ['captain', 'navigator']

function summaryResponse(summary) {
  return { data: { summary } }
}

function memoryResponse(characterId, memory_updates) {
  return { data: { character_id: characterId, memory_updates } }
}

function deferred() {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

function setup() {
  return renderHook(() =>
    useFinishDrafts({ storyId: 's1', sceneId: 1, participantIds: IDS })
  )
}

describe('useFinishDrafts', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('starts with idle empty tabs and all memory tabs unresolved', () => {
    const { result } = setup()

    expect(Object.keys(result.current.tabs)).toEqual([SUMMARY_TAB, ...IDS])
    expect(result.current.tabs[SUMMARY_TAB]).toEqual({
      items: [],
      status: 'idle',
      generated: false,
      error: null,
    })
    expect(result.current.unresolvedMemoryTabs).toEqual(IDS)
    expect(result.current.isGenerating).toBe(false)
  })

  it('generate stores the draft and marks the tab done', async () => {
    getCharacterMemoryDraft.mockResolvedValue(memoryResponse('captain', ['m1']))
    const { result } = setup()

    await act(() => result.current.generate('captain'))

    expect(getCharacterMemoryDraft).toHaveBeenCalledWith('s1', 1, 'captain')
    expect(result.current.tabs.captain).toEqual({
      items: ['m1'],
      status: 'done',
      generated: true,
      error: null,
    })
  })

  it('generate failure sets error status and keeps existing items', async () => {
    getCharacterSceneSummaryDraft.mockRejectedValue(new Error('boom'))
    const { result } = setup()
    act(() => result.current.setItems(SUMMARY_TAB, ['mine']))

    await act(() => result.current.generate(SUMMARY_TAB))

    expect(result.current.tabs[SUMMARY_TAB]).toEqual({
      items: ['mine'],
      status: 'error',
      generated: false,
      error: 'boom',
    })
  })

  it('reports generating while a request is pending', async () => {
    const pending = deferred()
    getCharacterSceneSummaryDraft.mockReturnValue(pending.promise)
    const { result } = setup()

    act(() => {
      result.current.generate(SUMMARY_TAB)
    })
    expect(result.current.isGenerating).toBe(true)

    await act(async () => pending.resolve(summaryResponse(['s'])))
    expect(result.current.isGenerating).toBe(false)
  })

  it('generateAll generates every empty tab', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue(summaryResponse(['s']))
    getCharacterMemoryDraft.mockImplementation(async (_s, _c, id) =>
      memoryResponse(id, [`${id}-m`])
    )
    const { result } = setup()

    await act(() => result.current.generateAll())

    expect(result.current.tabs[SUMMARY_TAB].items).toEqual(['s'])
    expect(result.current.tabs.captain.items).toEqual(['captain-m'])
    expect(result.current.tabs.navigator.items).toEqual(['navigator-m'])
  })

  it('generateAll skips done, generating and non-empty tabs and retries failed ones', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue(summaryResponse(['s']))
    getCharacterMemoryDraft.mockImplementation(async (_s, _c, id) =>
      memoryResponse(id, [`${id}-m`])
    )
    const { result } = setup()
    // summary: done, captain: error, navigator: typed text
    await act(() => result.current.generate(SUMMARY_TAB))
    getCharacterMemoryDraft.mockRejectedValueOnce(new Error('fail'))
    await act(() => result.current.generate('captain'))
    act(() => result.current.setItems('navigator', ['typed']))
    vi.clearAllMocks()
    getCharacterMemoryDraft.mockImplementation(async (_s, _c, id) =>
      memoryResponse(id, [`${id}-m`])
    )

    await act(() => result.current.generateAll())

    expect(getCharacterSceneSummaryDraft).not.toHaveBeenCalled()
    expect(getCharacterMemoryDraft.mock.calls).toEqual([['s1', 1, 'captain']])
    expect(result.current.tabs.navigator.items).toEqual(['typed'])
    expect(result.current.tabs.captain.status).toBe('done')
  })

  it('generateAll skips a tab that is already generating', async () => {
    const pending = deferred()
    getCharacterSceneSummaryDraft.mockReturnValue(pending.promise)
    getCharacterMemoryDraft.mockImplementation(async (_s, _c, id) =>
      memoryResponse(id, ['m'])
    )
    const { result } = setup()
    act(() => {
      result.current.generate(SUMMARY_TAB)
    })

    await act(() => result.current.generateAll())

    expect(getCharacterSceneSummaryDraft).toHaveBeenCalledTimes(1)
    await act(async () => pending.resolve(summaryResponse(['s'])))
  })

  it('generateAll skips a tab generated and then cleared', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue(summaryResponse(['s']))
    const { result } = setup()
    await act(() => result.current.generate(SUMMARY_TAB))
    act(() => result.current.setItems(SUMMARY_TAB, []))
    getCharacterMemoryDraft.mockResolvedValue(memoryResponse('x', []))

    await act(() => result.current.generateAll())

    expect(getCharacterSceneSummaryDraft).toHaveBeenCalledTimes(1)
  })

  it('regenerate overwrites edited content of a done tab', async () => {
    getCharacterSceneSummaryDraft
      .mockResolvedValueOnce(summaryResponse(['first']))
      .mockResolvedValueOnce(summaryResponse(['second']))
    const { result } = setup()
    await act(() => result.current.generate(SUMMARY_TAB))
    act(() => result.current.setItems(SUMMARY_TAB, ['edited']))

    await act(() => result.current.generate(SUMMARY_TAB))

    expect(result.current.tabs[SUMMARY_TAB].items).toEqual(['second'])
  })

  it('ignores results that arrive after reset', async () => {
    const pending = deferred()
    getCharacterSceneSummaryDraft.mockReturnValue(pending.promise)
    const { result } = setup()
    act(() => {
      result.current.generate(SUMMARY_TAB)
    })
    act(() => result.current.reset())

    await act(async () => pending.resolve(summaryResponse(['late'])))

    expect(result.current.tabs[SUMMARY_TAB]).toEqual({
      items: [],
      status: 'idle',
      generated: false,
      error: null,
    })
  })

  it('ignores errors that arrive after reset', async () => {
    const pending = deferred()
    getCharacterSceneSummaryDraft.mockReturnValue(pending.promise)
    const { result } = setup()
    act(() => {
      result.current.generate(SUMMARY_TAB)
    })
    act(() => result.current.reset())

    await act(async () => pending.reject(new Error('late')))

    expect(result.current.tabs[SUMMARY_TAB].status).toBe('idle')
  })

  it('ignores a result superseded by a newer request on the same tab', async () => {
    const first = deferred()
    const second = deferred()
    getCharacterSceneSummaryDraft
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
    const { result } = setup()
    act(() => {
      result.current.generate(SUMMARY_TAB)
    })
    act(() => {
      result.current.generate(SUMMARY_TAB)
    })

    await act(async () => second.resolve(summaryResponse(['new'])))
    await act(async () => first.resolve(summaryResponse(['old'])))

    expect(result.current.tabs[SUMMARY_TAB].items).toEqual(['new'])
  })

  it('treats a memory tab as resolved when generated, even if cleared', async () => {
    getCharacterMemoryDraft.mockResolvedValue(memoryResponse('captain', ['m']))
    const { result } = setup()
    await act(() => result.current.generate('captain'))

    act(() => result.current.setItems('captain', []))

    expect(result.current.unresolvedMemoryTabs).toEqual(['navigator'])
  })

  it('treats a memory tab with text as resolved', () => {
    const { result } = setup()

    act(() => result.current.setItems('navigator', ['typed']))

    expect(result.current.unresolvedMemoryTabs).toEqual(['captain'])
  })

  it('builds the finish payload keyed by participant with blanks removed', async () => {
    getCharacterSceneSummaryDraft.mockResolvedValue(summaryResponse([' s1 ', '']))
    const { result } = setup()
    await act(() => result.current.generate(SUMMARY_TAB))
    act(() => result.current.setItems('captain', ['  a ', '   ']))

    expect(result.current.buildPayload()).toEqual({
      sceneSummary: ['s1'],
      characterMemoryUpdates: { captain: ['a'], navigator: [] },
    })
  })
})
