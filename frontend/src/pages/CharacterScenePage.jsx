import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getCharacters } from '../api/characters'
import {
  deleteCharacterSceneItem,
  editCharacterSceneItem,
  finishCharacterScene,
  getCharacterScene,
  replaceCharacterTurn,
  submitCharacterTurn,
} from '../api/character_play'
import { getModels } from '../api/models'
import { getStory } from '../api/stories'
import SceneHeader from '../components/SceneHeader'
import StoryTimeline from '../components/StoryTimeline'
import TurnComposer, { PLAYER_ACTOR } from '../components/TurnComposer'
import CharacterFinishModal from '../components/CharacterFinishModal'
import { deriveModelDefaults } from './characterSceneHelpers'

function CharacterScenePage() {
  const navigate = useNavigate()
  const { storyId, sceneId } = useParams()
  const [scene, setScene] = useState(null)
  const [storyTitle, setStoryTitle] = useState('')
  const [characters, setCharacters] = useState([])
  const [models, setModels] = useState([])
  const [characterModelId, setCharacterModelId] = useState(null)
  const [narratorModelId, setNarratorModelId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actor, setActor] = useState(PLAYER_ACTOR)
  const [text, setText] = useState('')
  const [retryItemId, setRetryItemId] = useState(null)
  const [retryDraft, setRetryDraft] = useState(null)
  const [sending, setSending] = useState(false)
  const [turnError, setTurnError] = useState(null)
  const [itemOperationBusy, setItemOperationBusy] = useState(false)
  const [itemOperationError, setItemOperationError] = useState(null)
  const [showFinishModal, setShowFinishModal] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const [sceneResponse, storyResponse, charactersResponse, modelsResponse] =
          await Promise.all([
            getCharacterScene(storyId, sceneId),
            getStory(storyId),
            getCharacters(storyId),
            getModels(),
          ])
        const loadedScene = sceneResponse.data
        const registry = modelsResponse.data
        const modelDefaults = deriveModelDefaults(loadedScene.items ?? [], registry)

        setScene(loadedScene)
        setStoryTitle(storyResponse.data.title)
        setCharacters(charactersResponse.data)
        setModels(
          Object.entries(registry.models).map(([id, model]) => ({ id, ...model }))
        )
        setCharacterModelId(modelDefaults.characterModelId)
        setNarratorModelId(modelDefaults.narratorModelId)
      } catch (err) {
        setError(err.message ?? 'Failed to load scene')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [storyId, sceneId])

  async function handleSubmit() {
    const trimmed = text.trim()
    const isPlayer = actor === PLAYER_ACTOR
    if (isPlayer && !trimmed) return

    const payload = {
      actor: isPlayer ? { type: 'player' } : { type: 'character', character_id: actor },
      ...(isPlayer ? { action: trimmed } : { guidance: trimmed }),
      character_model_id: characterModelId,
      narrator_model_id: narratorModelId,
    }

    setTurnError(null)
    setSending(true)
    try {
      const response = retryItemId
        ? await replaceCharacterTurn(storyId, sceneId, retryItemId, payload)
        : await submitCharacterTurn(storyId, sceneId, payload)
      const item = response.data
      setScene((current) => ({
        ...current,
        items: retryItemId
          ? current.items.map((currentItem) =>
              currentItem.id === retryItemId ? item : currentItem
            )
          : [...(current.items ?? []), item],
      }))
      setText('')
      setActor(PLAYER_ACTOR)
      setRetryItemId(null)
      setRetryDraft(null)
      if (item.llm_data?.character_model_id != null) {
        setCharacterModelId(item.llm_data.character_model_id)
      }
      if (item.llm_data?.narrator_model_id != null) {
        setNarratorModelId(item.llm_data.narrator_model_id)
      }
    } catch (err) {
      setTurnError(err.message ?? 'Failed to submit turn')
    } finally {
      setSending(false)
    }
  }

  function handleRetry(item) {
    const isPlayer = item.actor?.type === 'player'
    setRetryDraft({ actor, text, characterModelId, narratorModelId })
    setRetryItemId(item.id)
    setActor(isPlayer ? PLAYER_ACTOR : item.actor.character_id)
    setText(isPlayer ? item.input?.action ?? '' : item.input?.guidance ?? '')
    setCharacterModelId(item.llm_data?.character_model_id ?? characterModelId)
    setNarratorModelId(item.llm_data?.narrator_model_id ?? narratorModelId)
    setTurnError(null)
  }

  function handleCancelRetry() {
    if (retryDraft) {
      setActor(retryDraft.actor)
      setText(retryDraft.text)
      setCharacterModelId(retryDraft.characterModelId)
      setNarratorModelId(retryDraft.narratorModelId)
    } else {
      setActor(PLAYER_ACTOR)
      setText('')
    }
    setRetryItemId(null)
    setRetryDraft(null)
    setTurnError(null)
  }

  async function handleEditItem(itemId, narration) {
    setItemOperationBusy(true)
    try {
      const response = await editCharacterSceneItem(storyId, sceneId, itemId, narration)
      setScene((current) => ({
        ...current,
        items: current.items.map((item) => item.id === itemId ? response.data : item),
      }))
    } finally {
      setItemOperationBusy(false)
    }
  }

  async function handleDeleteItem(itemId) {
    setItemOperationBusy(true)
    setItemOperationError(null)
    try {
      await deleteCharacterSceneItem(storyId, sceneId, itemId)
      setScene((current) => ({
        ...current,
        items: current.items.filter((item) => item.id !== itemId),
      }))
    } catch (err) {
      setItemOperationError(err.message ?? 'Failed to delete paragraph')
    } finally {
      setItemOperationBusy(false)
    }
  }

  async function handleFinish({ sceneSummary, characterMemoryUpdates }) {
    await finishCharacterScene(
      storyId,
      sceneId,
      sceneSummary,
      characterMemoryUpdates
    )
    navigate(`/stories/${storyId}`)
  }

  if (loading) return <p>Loading...</p>
  if (error) return <p className="scene-page__error">{error}</p>

  const characterNames = new Map(characters.map((character) => [character.id, character.name]))
  const nameOf = (id) => characterNames.get(id) ?? id
  const playerName = scene.user_character_id ? nameOf(scene.user_character_id) : 'Narrator'
  const npcCharacters = (scene.character_ids ?? []).map((id) => ({ id, name: nameOf(id) }))
  const npcNames = npcCharacters.map((character) => character.name)
  const participants = [
    ...(scene.user_character_id
      ? [{ id: scene.user_character_id, name: nameOf(scene.user_character_id) }]
      : []),
    ...npcCharacters,
  ]

  return (
    <div className="scene-page scene-page--fixed-frame">
      <SceneHeader
        scene={scene}
        storyId={storyId}
        storyTitle={storyTitle}
        models={models}
        selectedModelId={narratorModelId}
        onModelChange={setNarratorModelId}
        disabled={scene.finished || sending}
        modelLabel="LLM"
      />
      <p className="scene-page__participants">
        <span>Player: {playerName}</span>
        {npcNames.length > 0 && <span>Characters: {npcNames.join(', ')}</span>}
      </p>
      <div className="scene-page__messages" role="log" aria-label="Scene story">
        <StoryTimeline
          items={scene.items ?? []}
          onEdit={handleEditItem}
          onDelete={handleDeleteItem}
          onRetry={handleRetry}
          disabled={scene.finished || sending || itemOperationBusy}
          actionsDisabled={retryItemId !== null}
        />
      </div>
      <div className="scene-page__footer">
        {scene.finished ? (
          <p className="scene-page__finished" role="status">This scene is finished.</p>
        ) : (
          <>
            {itemOperationError && (
              <p className="scene-page__error" role="alert">{itemOperationError}</p>
            )}
            {turnError && <p className="scene-page__error" role="alert">{turnError}</p>}
            <TurnComposer
              actor={actor}
              onActorChange={setActor}
              characters={npcCharacters}
              text={text}
              onTextChange={setText}
              models={models}
              characterModelId={characterModelId}
              onCharacterModelChange={setCharacterModelId}
              onSubmit={handleSubmit}
              retrying={retryItemId !== null}
              onCancelRetry={handleCancelRetry}
              sending={sending}
              leadingAction={
                <button
                  type="button"
                  onClick={() => setShowFinishModal(true)}
                  disabled={sending || itemOperationBusy}
                >
                  Finish
                </button>
              }
            />
          </>
        )}
      </div>
      {showFinishModal && (
        <CharacterFinishModal
          storyId={storyId}
          sceneId={sceneId}
          participants={participants}
          onSubmit={handleFinish}
          onCancel={() => setShowFinishModal(false)}
        />
      )}
    </div>
  )
}

export default CharacterScenePage
