import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getCharacters } from '../api/characters'
import { createCharacterScene, getCharacterScene } from '../api/character_play'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import BulletTextarea from '../components/BulletTextarea'
import CharacterCheckboxList from '../components/CharacterCheckboxList'
import CharacterSelect from '../components/CharacterSelect'
import ModelSelect from '../components/ModelSelect'
import { inputBase } from '../styles'
import { buildScenePrefill, deriveModelDefaults } from './characterSceneHelpers'
import { updateParticipantSelection } from './participantSelection'

const NARRATOR_CHARACTER_ID = '__narrator__'

function NewCharacterScenePage() {
  const { storyId } = useParams()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [characters, setCharacters] = useState([])
  const [models, setModels] = useState([])
  const [submitError, setSubmitError] = useState(null)
  const [validationErrors, setValidationErrors] = useState({})
  const [busy, setBusy] = useState(false)

  const [playerCharacterId, setPlayerCharacterId] = useState('')
  const [characterIds, setCharacterIds] = useState([])
  const [context, setContext] = useState([])
  const [generalSceneGuide, setGeneralSceneGuide] = useState('')
  const [writingStyle, setWritingStyle] = useState('')
  const [firstMessage, setFirstMessage] = useState('')
  const [characterModelId, setCharacterModelId] = useState('')
  const [narratorModelId, setNarratorModelId] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [storyResponse, charactersResponse, modelsResponse] = await Promise.all([
          getStory(storyId),
          getCharacters(storyId),
          getModels(),
        ])
        const story = storyResponse.data
        const registry = modelsResponse.data
        const modelDefaults = deriveModelDefaults([], registry)

        setCharacters(charactersResponse.data)
        setModels(
          Object.entries(registry.models).map(([id, model]) => ({ id, ...model }))
        )
        setCharacterModelId(modelDefaults.characterModelId)
        setNarratorModelId(modelDefaults.narratorModelId)

        const previousScene = story.scenes.filter((scene) => scene.finished).at(-1)
        if (previousScene) {
          const sceneResponse = await getCharacterScene(storyId, previousScene.id)
          const previousSceneData = sceneResponse.data
          const prefill = buildScenePrefill(previousSceneData)
          const previousModelDefaults = deriveModelDefaults(
            previousSceneData.items ?? [],
            registry
          )

          setContext(prefill.context)
          setWritingStyle(prefill.writingStyle)
          setFirstMessage(prefill.firstMessage)
          setCharacterModelId(previousModelDefaults.characterModelId)
          setNarratorModelId(previousModelDefaults.narratorModelId)
        }
      } catch (err) {
        setLoadError(err.message ?? 'Failed to load page data')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [storyId])

  function handlePlayerChange(characterId) {
    const selection = updateParticipantSelection(
      { playerCharacterId, npcCharacterIds: characterIds },
      { type: 'player', characterId }
    )
    setPlayerCharacterId(selection.playerCharacterId)
    setCharacterIds(selection.npcCharacterIds)
  }

  function handleCharacterToggle(characterId) {
    const selection = updateParticipantSelection(
      { playerCharacterId, npcCharacterIds: characterIds },
      { type: 'npc', characterId }
    )
    setPlayerCharacterId(selection.playerCharacterId)
    setCharacterIds(selection.npcCharacterIds)
  }

  function validate() {
    const errors = {}
    if (!playerCharacterId) {
      errors.playerCharacterId = 'Player is required'
    }
    if (!context.some((item) => item.trim())) {
      errors.context = 'At least one context bullet is required'
    }
    if (!generalSceneGuide.trim()) {
      errors.generalSceneGuide = 'General scene guide is required'
    }
    if (!writingStyle.trim()) {
      errors.writingStyle = 'Writing style is required'
    }
    if (!firstMessage.trim()) {
      errors.firstMessage = 'Opening narrator paragraph is required'
    } else if (firstMessage.length > 4000) {
      errors.firstMessage = 'Opening narrator paragraph must be 4000 characters or fewer'
    }
    return errors
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitError(null)

    const errors = validate()
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors)
      return
    }
    setValidationErrors({})

    setBusy(true)
    try {
      const response = await createCharacterScene(storyId, {
        user_character_id:
          playerCharacterId === NARRATOR_CHARACTER_ID ? null : playerCharacterId,
        character_ids: characterIds,
        context,
        general_scene_guide: generalSceneGuide,
        writing_style: writingStyle,
        first_message: firstMessage,
        character_model_id: characterModelId,
        narrator_model_id: narratorModelId,
      })
      navigate(`/stories/${storyId}/character-scenes/${response.data.id}`)
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
      <h1 className="new-scene-page__heading">New Character-Driven Scene</h1>
      <form onSubmit={handleSubmit} className="new-scene-page__form">
        <fieldset className="new-scene-page__fieldset new-scene-page__section">
          <legend className="new-scene-page__legend">Participants</legend>
          <div className="new-scene-page__field">
            <CharacterSelect
              id="playerCharacter"
              label="Player"
              characters={characters}
              value={playerCharacterId}
              onChange={handlePlayerChange}
              includeNarrator
              narratorValue={NARRATOR_CHARACTER_ID}
              className="new-scene-page__select"
            />
            {validationErrors.playerCharacterId && (
              <p className="new-scene-page__error">{validationErrors.playerCharacterId}</p>
            )}
          </div>
          <CharacterCheckboxList
            label="Characters"
            characters={characters}
            selectedIds={characterIds}
            onToggle={handleCharacterToggle}
            disabledCharacterId={playerCharacterId}
          />
        </fieldset>

        <fieldset className="new-scene-page__fieldset new-scene-page__section">
          <legend className="new-scene-page__legend">Starting situation</legend>
          <div className="new-scene-page__field">
            <label htmlFor="context" className="new-scene-page__label">Context</label>
            <BulletTextarea
              id="context"
              value={context}
              onChange={setContext}
              rows={8}
              style={inputBase}
              className="new-scene-page__context-textarea"
            />
            {validationErrors.context && (
              <p className="new-scene-page__error">{validationErrors.context}</p>
            )}
          </div>
          <div className="new-scene-page__field">
            <label htmlFor="firstMessage" className="new-scene-page__label">
              Opening narrator paragraph
            </label>
            <textarea
              id="firstMessage"
              value={firstMessage}
              onChange={(event) => setFirstMessage(event.target.value)}
              maxLength={4000}
              rows={8}
              style={inputBase}
              className="new-scene-page__textarea"
            />
            {validationErrors.firstMessage && (
              <p className="new-scene-page__error">{validationErrors.firstMessage}</p>
            )}
          </div>
        </fieldset>

        <fieldset className="new-scene-page__fieldset new-scene-page__section">
          <legend className="new-scene-page__legend">Narrative direction</legend>
          <div className="new-scene-page__field">
            <label htmlFor="generalSceneGuide" className="new-scene-page__label">
              General scene guide
            </label>
            <textarea
              id="generalSceneGuide"
              value={generalSceneGuide}
              onChange={(event) => setGeneralSceneGuide(event.target.value)}
              rows={6}
              style={inputBase}
              className="new-scene-page__textarea"
            />
            {validationErrors.generalSceneGuide && (
              <p className="new-scene-page__error">{validationErrors.generalSceneGuide}</p>
            )}
          </div>
          <div className="new-scene-page__field">
            <label htmlFor="writingStyle" className="new-scene-page__label">Writing style</label>
            <textarea
              id="writingStyle"
              value={writingStyle}
              onChange={(event) => setWritingStyle(event.target.value)}
              rows={6}
              style={inputBase}
              className="new-scene-page__textarea"
            />
            {validationErrors.writingStyle && (
              <p className="new-scene-page__error">{validationErrors.writingStyle}</p>
            )}
          </div>
        </fieldset>

        <fieldset className="new-scene-page__fieldset new-scene-page__section">
          <legend className="new-scene-page__legend">Agents</legend>
          <ModelSelect
            id="characterModel"
            label="Character agent model"
            models={models}
            value={characterModelId}
            onChange={setCharacterModelId}
            className="new-scene-page__select"
          />
          <ModelSelect
            id="narratorModel"
            label="Narrator agent model"
            models={models}
            value={narratorModelId}
            onChange={setNarratorModelId}
            className="new-scene-page__select"
          />
        </fieldset>

        {submitError && <p className="new-scene-page__error">{submitError}</p>}

        <button type="submit" disabled={busy}>
          {busy ? 'Creating…' : 'Create scene'}
        </button>
      </form>
    </>
  )
}

export default NewCharacterScenePage
