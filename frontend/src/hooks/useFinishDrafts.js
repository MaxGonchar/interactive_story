import { useCallback, useMemo, useRef, useState } from 'react'
import {
  getCharacterMemoryDraft,
  getCharacterSceneSummaryDraft,
} from '../api/character_play'

export const SUMMARY_TAB = 'summary'

const EMPTY_TAB = { items: [], status: 'idle', generated: false, error: null }

function buildInitialState(participantIds) {
  const state = { [SUMMARY_TAB]: { ...EMPTY_TAB } }
  participantIds.forEach((id) => {
    state[id] = { ...EMPTY_TAB }
  })
  return state
}

function cleanItems(items) {
  return items.map((item) => item.trim()).filter((item) => item.length > 0)
}

function shouldGenerate(tab) {
  if (tab.status === 'generating' || tab.status === 'done') return false
  if (tab.status === 'error') return true
  return tab.items.length === 0
}

export function useFinishDrafts({ storyId, sceneId, participantIds }) {
  const idsKey = participantIds.join('\u0000')
  const [tabs, setTabs] = useState(() => buildInitialState(participantIds))
  const tabsRef = useRef(tabs)
  const epochRef = useRef(0)
  const requestRef = useRef({})

  const commit = useCallback((next) => {
    tabsRef.current = next
    setTabs(next)
  }, [])

  const patchTab = useCallback(
    (tabId, patch) => {
      const current = tabsRef.current[tabId]
      if (!current) return
      commit({ ...tabsRef.current, [tabId]: { ...current, ...patch } })
    },
    [commit]
  )

  // Bumping the epoch invalidates every in-flight request.
  const reset = useCallback(() => {
    epochRef.current += 1
    requestRef.current = {}
    commit(buildInitialState(participantIds))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [commit, idsKey])

  const generate = useCallback(
    async (tabId) => {
      if (!tabsRef.current[tabId]) return
      const epoch = epochRef.current
      const requestId = (requestRef.current[tabId] ?? 0) + 1
      requestRef.current[tabId] = requestId
      const isCurrent = () =>
        epochRef.current === epoch && requestRef.current[tabId] === requestId

      patchTab(tabId, { status: 'generating', error: null })
      try {
        const items =
          tabId === SUMMARY_TAB
            ? (await getCharacterSceneSummaryDraft(storyId, sceneId)).data.summary
            : (await getCharacterMemoryDraft(storyId, sceneId, tabId)).data
                .memory_updates
        if (!isCurrent()) return
        patchTab(tabId, { items, status: 'done', generated: true, error: null })
      } catch (err) {
        if (!isCurrent()) return
        patchTab(tabId, { status: 'error', error: err.message })
      }
    },
    [patchTab, storyId, sceneId]
  )

  const generateAll = useCallback(
    () =>
      Promise.all(
        Object.keys(tabsRef.current)
          .filter((tabId) => shouldGenerate(tabsRef.current[tabId]))
          .map((tabId) => generate(tabId))
      ),
    [generate]
  )

  const setItems = useCallback(
    (tabId, items) => patchTab(tabId, { items }),
    [patchTab]
  )

  const unresolvedMemoryTabs = useMemo(
    () =>
      participantIds.filter((id) => {
        const tab = tabs[id]
        return tab && !tab.generated && cleanItems(tab.items).length === 0
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tabs, idsKey]
  )

  const isGenerating = Object.values(tabs).some(
    (tab) => tab.status === 'generating'
  )

  const buildPayload = useCallback(() => {
    const current = tabsRef.current
    const characterMemoryUpdates = {}
    participantIds.forEach((id) => {
      characterMemoryUpdates[id] = cleanItems(current[id]?.items ?? [])
    })
    return {
      sceneSummary: cleanItems(current[SUMMARY_TAB].items),
      characterMemoryUpdates,
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey])

  return {
    tabs,
    isGenerating,
    unresolvedMemoryTabs,
    setItems,
    generate,
    generateAll,
    reset,
    buildPayload,
  }
}
