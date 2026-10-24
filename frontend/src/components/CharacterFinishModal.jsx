import { useState } from 'react'
import BulletTextarea from './BulletTextarea'
import { SUMMARY_TAB, useFinishDrafts } from '../hooks/useFinishDrafts'

const SUMMARY_MIN = 1
const SUMMARY_MAX = 100

function countItems(items) {
  return items.filter((item) => item.trim().length > 0).length
}

function badgeFor(tab) {
  if (tab.status === 'generating') return { label: 'Generating', kind: 'generating' }
  if (tab.status === 'error') return { label: 'Error', kind: 'error' }
  if (tab.status === 'done') return { label: 'Generated', kind: 'done' }
  if (countItems(tab.items) > 0) return { label: 'Edited', kind: 'edited' }
  return { label: 'Empty', kind: 'empty' }
}

// participants: ordered [{ id, name }] — player character first, then NPCs.
// onSubmit({ sceneSummary, characterMemoryUpdates }) may return a promise; a rejection is shown inline.
function CharacterFinishModal({ storyId, sceneId, participants, onSubmit, onCancel }) {
  const participantIds = participants.map((p) => p.id)
  const drafts = useFinishDrafts({ storyId, sceneId, participantIds })
  const { tabs, isGenerating, unresolvedMemoryTabs } = drafts

  const [activeTab, setActiveTab] = useState(SUMMARY_TAB)
  const [validationError, setValidationError] = useState(null)
  const [submitError, setSubmitError] = useState(null)
  const [confirmPending, setConfirmPending] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const tabList = [
    { id: SUMMARY_TAB, name: 'Summary' },
    ...participants.map((p) => ({ id: p.id, name: p.name })),
  ]
  const active = tabs[activeTab]
  const activeName = tabList.find((t) => t.id === activeTab)?.name

  function clearWarnings() {
    setConfirmPending(false)
    setValidationError(null)
  }

  function handleEdit(items) {
    clearWarnings()
    drafts.setItems(activeTab, items)
  }

  function handleGenerate(tabId) {
    clearWarnings()
    drafts.generate(tabId)
  }

  function handleGenerateAll() {
    clearWarnings()
    drafts.generateAll()
  }

  function handleCancel() {
    drafts.reset()
    onCancel()
  }

  async function handleFinish() {
    const { sceneSummary, characterMemoryUpdates } = drafts.buildPayload()
    if (sceneSummary.length < SUMMARY_MIN) {
      setValidationError('Please add at least 1 summary item.')
      return
    }
    if (sceneSummary.length > SUMMARY_MAX) {
      setValidationError('Summary cannot exceed 100 items.')
      return
    }
    setValidationError(null)

    if (unresolvedMemoryTabs.length > 0 && !confirmPending) {
      setConfirmPending(true)
      return
    }

    setSubmitError(null)
    setIsSubmitting(true)
    try {
      await onSubmit({ sceneSummary, characterMemoryUpdates })
    } catch (err) {
      setSubmitError(err?.message ?? 'Failed to finish the scene.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const unresolvedNames = unresolvedMemoryTabs
    .map((id) => participants.find((p) => p.id === id)?.name)
    .filter(Boolean)
    .join(', ')

  return (
    <div className="modal-overlay">
      <div className="modal-panel finish-modal__panel">
        <h3 className="finish-modal__title">Finish Scene</h3>
        <div role="tablist" aria-label="Finish scene sections" className="finish-modal__tabs">
          {tabList.map((tab) => {
            const badge = badgeFor(tabs[tab.id])
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                id={`finish-tab-${tab.id}`}
                aria-selected={tab.id === activeTab}
                aria-controls="finish-tabpanel"
                className="finish-modal__tab"
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.name}
                <span className={`finish-modal__badge finish-modal__badge--${badge.kind}`}>
                  {badge.label}
                </span>
              </button>
            )
          })}
        </div>
        <div
          role="tabpanel"
          id="finish-tabpanel"
          aria-labelledby={`finish-tab-${activeTab}`}
          className="finish-modal__panel-body"
        >
          <BulletTextarea
            key={activeTab}
            aria-label={`${activeName} editor`}
            className="finish-modal__editor"
            value={active.items}
            onChange={handleEdit}
            disabled={active.status === 'generating'}
            rows={12}
          />
          {active.status === 'generating' && (
            <p className="finish-modal__status" role="status">
              Generating {activeName}…
            </p>
          )}
          {active.status === 'error' && (
            <p className="finish-modal__error" role="alert">
              {active.error}
            </p>
          )}
        </div>
        {validationError && (
          <p className="finish-modal__error" role="alert">
            {validationError}
          </p>
        )}
        {confirmPending && unresolvedMemoryTabs.length > 0 && (
          <p className="finish-modal__status" role="alert">
            No memory update was generated or entered for: {unresolvedNames}. Select Finish
            scene again to confirm.
          </p>
        )}
        {submitError && (
          <p className="finish-modal__error" role="alert">
            {submitError}
          </p>
        )}
        <div className="finish-modal__actions">
          <button type="button" onClick={handleGenerateAll}>
            Generate all
          </button>
          <button type="button" onClick={() => handleGenerate(activeTab)}>
            Regenerate this
          </button>
          <div className="finish-modal__spacer">
            <button type="button" onClick={handleCancel}>
              Cancel
            </button>
            <button type="button" onClick={handleFinish} disabled={isGenerating || isSubmitting}>
              Finish scene
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CharacterFinishModal
