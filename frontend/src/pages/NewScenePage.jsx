import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getStory } from '../api/stories'
import { getScene, createScene } from '../api/scenes'
import { getCharacters } from '../api/characters'
import BulletTextarea from '../components/BulletTextarea'

function NewScenePage() {
  const { storyId } = useParams()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [characters, setCharacters] = useState([])
  const [submitError, setSubmitError] = useState(null)
  const [validationErrors, setValidationErrors] = useState({})
  const [busy, setBusy] = useState(false)

  const [userCharacterId, setUserCharacterId] = useState('')
  const [sceneCharacterIds, setSceneCharacterIds] = useState([])
  const [context, setContext] = useState([])
  const [generalSceneGuide, setGeneralSceneGuide] = useState('')
  const [writingStyle, setWritingStyle] = useState('')
  const [firstMessage, setFirstMessage] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [storyResponse, charactersResponse] = await Promise.all([
          getStory(storyId),
          getCharacters(storyId),
        ])
        const story = storyResponse.data
        setCharacters(charactersResponse.data)

        const finishedScenes = story.scenes.filter((s) => s.finished)
        if (finishedScenes.length > 0) {
          const lastScene = finishedScenes[finishedScenes.length - 1]
          const sceneResponse = await getScene(storyId, lastScene.id)
          const sceneData = sceneResponse.data

          if (sceneData.scene_summary) {
            setContext(sceneData.scene_summary)
          }
          if (sceneData.scene_description?.writing_style) {
            setWritingStyle(sceneData.scene_description.writing_style)
          }
          const assistantMessages = sceneData.messages.filter(
            (m) => m.role === 'assistant'
          )
          if (assistantMessages.length > 0) {
            setFirstMessage(assistantMessages[assistantMessages.length - 1].content)
          }
        }
      } catch (err) {
        setLoadError(err.message ?? 'Failed to load page data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [storyId])

  function handleUserCharacterChange(characterId) {
    setUserCharacterId(characterId)
    setSceneCharacterIds((prev) => prev.filter((id) => id !== characterId))
  }

  function handleSceneCharacterToggle(characterId) {
    setSceneCharacterIds((prev) => {
      if (prev.includes(characterId)) {
        return prev.filter((id) => id !== characterId)
      }
      return [...prev, characterId]
    })
    if (userCharacterId === characterId) {
      setUserCharacterId('')
    }
  }

  function validate() {
    const errors = {}
    if (!userCharacterId) {
      errors.userCharacterId = 'User character is required'
    }
    if (context.length === 0) {
      errors.context = 'At least one context bullet is required'
    }
    if (!generalSceneGuide.trim()) {
      errors.generalSceneGuide = 'General scene guide is required'
    }
    if (!writingStyle.trim()) {
      errors.writingStyle = 'Writing style is required'
    }
    if (!firstMessage.trim()) {
      errors.firstMessage = 'First message is required'
    }
    return errors
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitError(null)

    const errors = validate()
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors)
      return
    }
    setValidationErrors({})

    setBusy(true)
    try {
      const response = await createScene(storyId, {
        user_character_id: userCharacterId,
        character_ids: sceneCharacterIds,
        context,
        general_scene_guide: generalSceneGuide,
        writing_style: writingStyle,
        first_message: firstMessage,
      })
      navigate(`/stories/${storyId}/scenes/${response.data.id}`)
    } catch (err) {
      setSubmitError(err.message ?? 'Failed to create scene')
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return <p>Loading...</p>
  }

  if (loadError) {
    return <p>{loadError}</p>
  }

  return (
    <>
      <h1>New Scene</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="userCharacter">User character</label>
          <select
            id="userCharacter"
            value={userCharacterId}
            onChange={(e) => handleUserCharacterChange(e.target.value)}
          >
            <option value="">— select —</option>
            {characters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          {validationErrors.userCharacterId && (
            <span>{validationErrors.userCharacterId}</span>
          )}
        </div>

        <div>
          <fieldset>
            <legend>Scene characters</legend>
            {characters.map((c) => (
              <label key={c.id}>
                <input
                  type="checkbox"
                  checked={sceneCharacterIds.includes(c.id)}
                  disabled={c.id === userCharacterId}
                  onChange={() => handleSceneCharacterToggle(c.id)}
                />
                {c.name}
              </label>
            ))}
          </fieldset>
        </div>

        <div>
          <label htmlFor="context">Context</label>
          <BulletTextarea
            id="context"
            value={context}
            onChange={setContext}
            rows={6}
          />
          {validationErrors.context && (
            <span>{validationErrors.context}</span>
          )}
        </div>

        <div>
          <label htmlFor="generalSceneGuide">General scene guide</label>
          <textarea
            id="generalSceneGuide"
            value={generalSceneGuide}
            onChange={(e) => setGeneralSceneGuide(e.target.value)}
            rows={4}
          />
          {validationErrors.generalSceneGuide && (
            <span>{validationErrors.generalSceneGuide}</span>
          )}
        </div>

        <div>
          <label htmlFor="writingStyle">Writing style</label>
          <textarea
            id="writingStyle"
            value={writingStyle}
            onChange={(e) => setWritingStyle(e.target.value)}
            rows={3}
          />
          {validationErrors.writingStyle && (
            <span>{validationErrors.writingStyle}</span>
          )}
        </div>

        <div>
          <label htmlFor="firstMessage">First message</label>
          <textarea
            id="firstMessage"
            value={firstMessage}
            onChange={(e) => setFirstMessage(e.target.value)}
            rows={5}
          />
          {validationErrors.firstMessage && (
            <span>{validationErrors.firstMessage}</span>
          )}
        </div>

        {submitError && <p>{submitError}</p>}

        <button type="submit" disabled={busy}>
          {busy ? 'Creating…' : 'Create scene'}
        </button>
      </form>
    </>
  )
}

export default NewScenePage
