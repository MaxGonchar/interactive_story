import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  getChoiceDrivenPlay,
  generateChoices,
  regenerateChoices,
  selectChoice,
  editStepText,
  returnToStep,
} from '../api/choice_driven'
import StepItem from '../components/StepItem'
import ChoicesGrid from '../components/ChoicesGrid'
import ProcessingLabel from '../components/ProcessingLabel'

function ChoiceDrivenStoryPage() {
  const { storyId } = useParams()
  const [title, setTitle] = useState('')
  const [steps, setSteps] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const [opError, setOpError] = useState(null)
  const [pendingAction, setPendingAction] = useState(null)

  useEffect(() => {
    getChoiceDrivenPlay(storyId)
      .then((response) => {
        setTitle(response.data.title)
        setSteps(response.data.steps)
      })
      .catch((err) => setError(err.message ?? 'Failed to load story'))
      .finally(() => setLoading(false))
  }, [storyId])

  async function handleGenerateChoices() {
    setOpError(null)
    setBusy(true)
    setPendingAction('generate')
    try {
      const response = await generateChoices(storyId)
      const choices = response.data.choices
      setSteps((prev) =>
        prev.map((s, i) => (i === prev.length - 1 ? { ...s, choices } : s))
      )
    } catch (err) {
      setOpError(err.message ?? 'Failed to generate choices')
    } finally {
      setBusy(false)
      setPendingAction(null)
    }
  }

  async function handleRegenerateChoices() {
    setOpError(null)
    setBusy(true)
    setPendingAction('regenerate')
    try {
      const response = await regenerateChoices(storyId)
      const choices = response.data.choices
      setSteps((prev) =>
        prev.map((s, i) => (i === prev.length - 1 ? { ...s, choices } : s))
      )
    } catch (err) {
      setOpError(err.message ?? 'Failed to regenerate choices')
    } finally {
      setBusy(false)
      setPendingAction(null)
    }
  }

  async function handleSelectChoice(action, consequence) {
    setOpError(null)
    const choiceKey = `${action}::${consequence}`
    setBusy(true)
    setPendingAction(choiceKey)
    try {
      const response = await selectChoice(storyId, action, consequence)
      setSteps((prev) => [...prev, response.data])
    } catch (err) {
      setOpError(err.message ?? 'Failed to select choice')
    } finally {
      setBusy(false)
      setPendingAction(null)
    }
  }

  async function handleEditStep(stepId, text) {
    setOpError(null)
    try {
      const response = await editStepText(storyId, stepId, text)
      setSteps((prev) =>
        prev.map((s) => (s.id === stepId ? { ...s, text: response.data.text } : s))
      )
    } catch (err) {
      setOpError(err.message ?? 'Failed to edit step')
      throw err
    }
  }

  async function handleReturnToStep(stepId) {
    setOpError(null)
    setBusy(true)
    try {
      await returnToStep(storyId, stepId)
      setSteps((prev) => prev.filter((s) => s.id <= stepId))
    } catch (err) {
      setOpError(err.message ?? 'Failed to return to step')
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <p>Loading...</p>
  if (error) return <p>{error}</p>

  const lastStep = steps[steps.length - 1]
  const hasChoices = lastStep && lastStep.choices.length > 0

  return (
    <>
      <h1>{title}</h1>
      {opError && <p style={{ margin: 0, color: 'var(--error)', fontSize: '14px' }}>{opError}</p>}
      <div>
        {steps.map((step) => (
          <StepItem
            key={step.id}
            step={step}
            onEdit={handleEditStep}
            onReturn={handleReturnToStep}
            disabled={busy}
          />
        ))}
      </div>
      {lastStep && (
        hasChoices ? (
          <ChoicesGrid
            choices={lastStep.choices}
            onSelect={handleSelectChoice}
            onRegenerate={handleRegenerateChoices}
            disabled={busy}
            pendingAction={pendingAction}
          />
        ) : (
          <button
            onClick={handleGenerateChoices}
            disabled={busy}
            style={{ marginTop: '16px', minWidth: '150px' }}
          >
            {pendingAction === 'generate' ? <ProcessingLabel verb="Generating" /> : 'Generate choices'}
          </button>
        )
      )}
    </>
  )
}

export default ChoiceDrivenStoryPage
