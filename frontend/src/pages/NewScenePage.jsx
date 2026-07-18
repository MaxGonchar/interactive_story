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
            const previousContext = sceneData.context ?? []
            const summary = sceneData.scene_summary ?? []
            setContext([...previousContext, ...summary])
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

  const fieldStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  }

  const labelStyle = {
    color: 'var(--text-h)',
    fontFamily: 'var(--sans)',
    fontWeight: 600,
    alignSelf: 'flex-start',
  }

  const inputBaseStyle = {
    fontFamily: 'var(--sans)',
    fontSize: '16px',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '8px',
    resize: 'vertical',
    color: 'var(--text)',
    background: 'var(--bg)',
  }

  const errorStyle = {
    margin: 0,
    color: 'var(--error)',
    fontSize: '14px',
    alignSelf: 'flex-start',
  }

  return (
    <>
      <h1 style={{ color: 'var(--text-h)' }}>New Scene</h1>
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '24px',
          paddingBottom: '40px',
        }}
      >
        <div style={fieldStyle}>
          <label htmlFor="userCharacter" style={labelStyle}>User character</label>
          <select
            id="userCharacter"
            value={userCharacterId}
            onChange={(e) => handleUserCharacterChange(e.target.value)}
            style={{ ...inputBaseStyle, width: '300px' }}
          >
            <option value="">— select —</option>
            {characters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          {validationErrors.userCharacterId && (
            <p style={errorStyle}>{validationErrors.userCharacterId}</p>
          )}
        </div>

        <div style={fieldStyle}>
          <fieldset
            style={{
              border: '1px solid var(--border)',
              borderRadius: '4px',
              padding: '12px 16px',
              fontFamily: 'var(--sans)',
              color: 'var(--text)',
            }}
          >
            <legend style={{ color: 'var(--text-h)', fontWeight: 600 }}>Scene characters</legend>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {characters.map((c) => (
                <label key={c.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={sceneCharacterIds.includes(c.id)}
                    disabled={c.id === userCharacterId}
                    onChange={() => handleSceneCharacterToggle(c.id)}
                  />
                  {c.name}
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        <div style={fieldStyle}>
          <label htmlFor="context" style={labelStyle}>Context</label>
          <BulletTextarea
            id="context"
            value={context}
            onChange={setContext}
            rows={20}
            style={{ ...inputBaseStyle, width: '800px' }}
          />
          {validationErrors.context && (
            <p style={errorStyle}>{validationErrors.context}</p>
          )}
        </div>

        <div style={fieldStyle}>
          <label htmlFor="generalSceneGuide" style={labelStyle}>General scene guide</label>
          <textarea
            id="generalSceneGuide"
            value={generalSceneGuide}
            onChange={(e) => setGeneralSceneGuide(e.target.value)}
            rows={6}
            style={{ ...inputBaseStyle, width: '600px' }}
          />
          {validationErrors.generalSceneGuide && (
            <p style={errorStyle}>{validationErrors.generalSceneGuide}</p>
          )}
        </div>

        <div style={fieldStyle}>
          <label htmlFor="writingStyle" style={labelStyle}>Writing style</label>
          <textarea
            id="writingStyle"
            value={writingStyle}
            onChange={(e) => setWritingStyle(e.target.value)}
            rows={6}
            style={{ ...inputBaseStyle, width: '600px' }}
          />
          {validationErrors.writingStyle && (
            <p style={errorStyle}>{validationErrors.writingStyle}</p>
          )}
        </div>

        <div style={fieldStyle}>
          <label htmlFor="firstMessage" style={labelStyle}>First message</label>
          <textarea
            id="firstMessage"
            value={firstMessage}
            onChange={(e) => setFirstMessage(e.target.value)}
            rows={8}
            style={{ ...inputBaseStyle, width: '600px' }}
          />
          {validationErrors.firstMessage && (
            <p style={errorStyle}>{validationErrors.firstMessage}</p>
          )}
        </div>

        {submitError && <p style={{ margin: 0, color: 'var(--error)', fontSize: '14px' }}>{submitError}</p>}

        <button type="submit" disabled={busy}>
          {busy ? 'Creating…' : 'Create scene'}
        </button>
      </form>
    </>
  )
}

export default NewScenePage
